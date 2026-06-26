from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Resume, Analysis, JobDescription
from app.core.dependencies import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])

@router.get("/stats")
def get_admin_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Returns system analytics for the admin dashboard.
    """
    total_users = db.query(User).count()
    total_resumes = db.query(Resume).count()
    total_analyses = db.query(Analysis).count()
    total_jobs = db.query(JobDescription).count()

    return {
        "status": "ok",
        "metrics": {
            "total_users": total_users,
            "total_resumes_uploaded": total_resumes,
            "total_analyses_performed": total_analyses,
            "total_jobs_saved": total_jobs
        }
    }
