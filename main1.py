from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uuid
from database import SessionLocal, ESGJob, JobStatus
from worker import q, process_esg_article

app = FastAPI(title="Autonomous ESG Tracker API")

class AnalyzeRequest(BaseModel):
    url: str

@app.post("/analyze")
async def start_analysis(request: AnalyzeRequest):
    job_id = str(uuid.uuid4())
    
    # 1. Create record in DB
    db = SessionLocal()
    new_job = ESGJob(id=job_id, url=request.url, status=JobStatus.PENDING)
    db.add(new_job)
    db.commit()
    db.close()

    # 2. Push to Redis Queue
    q.enqueue(process_esg_article, job_id, request.url)

    return {"job_id": job_id, "message": "Analysis started in background"}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    db = SessionLocal()
    job = db.query(ESGJob).filter(ESGJob.id == job_id).first()
    db.close()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return {
        "id": job.id,
        "status": job.status,
        "result": job.result
    }