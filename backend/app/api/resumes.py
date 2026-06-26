import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.models import Resume, User
from app.schemas.resume import ResumeOut, ResumeDetailOut
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.services.pdf_extractor import extract_text_from_pdf

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])

def validate_and_save_pdf(file: UploadFile, user_id: int) -> tuple[str, str, str]:
    """
    Validates file size/type and saves it. Returns (filename, saved_path, extracted_text).
    """
    # 1. Type validation
    if not file.filename.lower().endswith(".pdf") and file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File {file.filename} is not a valid PDF document."
        )

    # 2. Read file in memory for size check and extraction
    try:
        content = file.file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read upload stream: {str(e)}"
        )
        
    # Check file size (e.g. 10MB limit)
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File {file.filename} size ({size_mb:.2f}MB) exceeds limit of {settings.MAX_FILE_SIZE_MB}MB."
        )

    # Extract text from pdf
    extracted_text = extract_text_from_pdf(content)

    # 3. Secure disk storage naming
    unique_filename = f"user_{user_id}_{uuid.uuid4().hex[:10]}_{file.filename}"
    save_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    try:
        with open(save_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write file to storage: {str(e)}"
        )

    return file.filename, save_path, extracted_text


@router.post("/upload", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    original_name, saved_path, extracted_text = validate_and_save_pdf(file, current_user.id)
    
    db_resume = Resume(
        user_id=current_user.id,
        filename=original_name,
        file_path=saved_path,
        raw_text=extracted_text
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    
    # Return mapping matching schema
    return ResumeOut(
        id=db_resume.id,
        filename=db_resume.filename,
        uploaded_at=db_resume.uploaded_at,
        text_length=len(db_resume.raw_text or "")
    )


@router.post("/upload-multiple", response_model=List[ResumeOut], status_code=status.HTTP_201_CREATED)
def upload_multiple_resumes(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    saved_resumes = []
    for file in files:
        try:
            original_name, saved_path, extracted_text = validate_and_save_pdf(file, current_user.id)
            db_resume = Resume(
                user_id=current_user.id,
                filename=original_name,
                file_path=saved_path,
                raw_text=extracted_text
            )
            db.add(db_resume)
            saved_resumes.append(db_resume)
        except HTTPException as e:
            # Continue or raise? For safety let's raise
            db.rollback()
            raise e
            
    db.commit()
    for r in saved_resumes:
        db.refresh(r)
        
    return [
        ResumeOut(
            id=r.id,
            filename=r.filename,
            uploaded_at=r.uploaded_at,
            text_length=len(r.raw_text or "")
        ) for r in saved_resumes
    ]


@router.get("", response_model=List[ResumeOut])
def list_resumes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.uploaded_at.desc()).all()
    return [
        ResumeOut(
            id=r.id,
            filename=r.filename,
            uploaded_at=r.uploaded_at,
            text_length=len(r.raw_text or "")
        ) for r in resumes
    ]


@router.get("/{resume_id}", response_model=ResumeDetailOut)
def get_resume(resume_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_200_OK)
def delete_resume(resume_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    # Delete underlying file
    if os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except Exception as e:
            # Log error but proceed with DB delete
            pass
            
    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted successfully"}
