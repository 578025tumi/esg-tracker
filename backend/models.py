import enum
import datetime
from sqlalchemy import Column, String, JSON, DateTime, Enum
from database import Base

# Define the status options for our background tasks
class JobStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ESGJob(Base):
    __tablename__ = "esg_jobs"

    id = Column(String, primary_key=True, index=True) # UUID string
    url = Column(String, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    
    # This stores the JSON output from the AI (summary, scores, etc.)
    result = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<ESGJob(id={self.id}, status={self.status})>"