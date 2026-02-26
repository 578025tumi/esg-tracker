from redis import Redis
from rq import Queue, Worker
from database import SessionLocal, ESGJob, JobStatus
from processor import analyze_news_content
from scraper import ESGScraper

redis_conn = Redis(host='localhost', port=6379)
q = Queue(connection=redis_conn)
scraper = ESGScraper()

def process_esg_article(job_id: str, url: str):
    db = SessionLocal()
    try:
        # 1. Update status to Processing
        job = db.query(ESGJob).filter(ESGJob.id == job_id).first()
        job.status = JobStatus.PROCESSING
        db.commit()

        # 2. Scrape and Analyze
        raw_text = scraper.fetch_article_text(url)
        analysis = analyze_news_content(raw_text)

        # 3. Save result and mark Completed
        job.result = analysis.model_dump()
        job.status = JobStatus.COMPLETED
        db.commit()
    except Exception as e:
        job.status = JobStatus.FAILED
        db.commit()
        print(f"Job {job_id} failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    worker = Worker([q], connection=redis_conn)
    worker.work()