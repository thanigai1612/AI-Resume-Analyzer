from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.models import JobDescription, User
from app.schemas.resume import JobDescriptionCreate, JobDescriptionOut
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/jobs", tags=["Job Descriptions"])

@router.post("", response_model=JobDescriptionOut, status_code=status.HTTP_201_CREATED)
def create_job_description(
    job_in: JobDescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_job = JobDescription(
        user_id=current_user.id,
        title=job_in.title,
        description_text=job_in.description_text
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@router.get("", response_model=List[JobDescriptionOut])
def list_job_descriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    jobs = db.query(JobDescription).filter(JobDescription.user_id == current_user.id).order_by(JobDescription.created_at.desc()).all()
    return jobs

@router.get("/{job_id}", response_model=JobDescriptionOut)
def get_job_description(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(JobDescription).filter(JobDescription.id == job_id, JobDescription.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    return job

@router.delete("/{job_id}", status_code=status.HTTP_200_OK)
def delete_job_description(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(JobDescription).filter(JobDescription.id == job_id, JobDescription.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    db.delete(job)
    db.commit()
    return {"message": "Job description deleted successfully"}
