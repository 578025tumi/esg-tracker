from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid
from database import get_db
from models import ESGJob, JobStatus
from processor import analyze_news_content  # Import directly
from scraper import ESGScraper            # Import directly
import datetime

app = FastAPI(title="Autonomous ESG Tracker")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Allow your Next.js app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
scraper = ESGScraper()

# This is the function that will run in the background
def background_processing_task(job_id: str, url: str, db_session_factory):
    db = db_session_factory()
    try:
        print(f"🔄 Starting job {job_id}")
        job = db.query(ESGJob).filter(ESGJob.id == job_id).first()
        
        # 1. Scrape
        # 1. Scrape
        raw_text = scraper.fetch_article_text(url)
        
        # ADD THIS CHECK:
        if "404" in raw_text or not raw_text:
             analysis_dict = {
                "summary": "We couldn't reach that URL. Please check the link and try again.",
                "impacts": [{"category": "Error", "impact_score": 0, "justification": "The scraper received a 404 Not Found error."}],
                "source_reliability": 0.0
            }
        else:
             # 3. Analyze (Real AI call)
             analysis_dict = analyze_news_content(raw_text)
        
        # 2. Update status to Processing
        job.status = JobStatus.PROCESSING
        db.commit()

        # 3. Analyze (This now returns a DICT)
        analysis_dict = analyze_news_content(raw_text)

        # 4. Save result and mark Completed
        job.result = analysis_dict # SQLAlchemy loves dicts for JSON columns
        job.status = JobStatus.COMPLETED
        db.commit()
        print(f"✅ Job {job_id} successfully saved to Supabase!")

    except Exception as e:
        print(f"💥 CRITICAL TASK FAILURE: {str(e)}")
        job = db.query(ESGJob).filter(ESGJob.id == job_id).first()
        if job:
            job.status = JobStatus.FAILED
            db.commit()
    finally:
        db.close()

@app.post("/analyze")
async def start_analysis(
    request: dict, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    url = request.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    job_id = str(uuid.uuid4())
    
    # Create record in Supabase
    new_job = ESGJob(id=job_id, url=url, status=JobStatus.PENDING)
    db.add(new_job)
    db.commit()

    # Launch the background task (Windows-friendly!)
    # We pass SessionLocal (the factory) rather than 'db' to avoid thread issues
    from database import SessionLocal
    background_tasks.add_task(background_processing_task, job_id, url, SessionLocal)

    return {"job_id": job_id, "message": "Analysis started in background"}

@app.get("/status/{job_id}")
async def get_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(ESGJob).filter(ESGJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # IMPORTANT: Use .value to ensure it returns "completed" (string) 
    # and not JobStatus.COMPLETED (object)
    current_status = job.status.value if hasattr(job.status, 'value') else str(job.status)
    
    print(f"🔍 Polling Check: Job {job_id} is currently {current_status}")

    return {
        "id": job.id,
        "status": current_status, 
        "result": job.result
    }