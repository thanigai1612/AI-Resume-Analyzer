from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.models import Resume, JobDescription, ChatHistory, User
from app.schemas.resume import (
    ChatRequest, ChatMessageOut, CoverLetterResponse, 
    InterviewQuestionsResponse, LinkedInSummaryResponse, 
    RewriteSectionResponse, RoadmapResponse
)
from app.core.dependencies import get_current_user
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/analysis", tags=["AI Assistant"])

def get_resume_and_job(resume_id: int, job_id: int | None, current_user: User, db: Session):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    job_text = ""
    if job_id:
        job = db.query(JobDescription).filter(JobDescription.id == job_id, JobDescription.user_id == current_user.id).first()
        if job:
            job_text = job.description_text
            
    return resume, job_text


@router.post("/{resume_id}/cover-letter", response_model=CoverLetterResponse)
def generate_cover_letter(
    resume_id: int, 
    job_description_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume, job_text = get_resume_and_job(resume_id, job_description_id, current_user, db)
    return AIService.generate_cover_letter(resume.raw_text or "", job_text, current_user.api_key_preference)


@router.post("/{resume_id}/interview", response_model=InterviewQuestionsResponse)
def generate_interview_questions(
    resume_id: int, 
    job_description_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume, job_text = get_resume_and_job(resume_id, job_description_id, current_user, db)
    return AIService.generate_interview_questions(resume.raw_text or "", job_text, current_user.api_key_preference)


@router.post("/{resume_id}/linkedin", response_model=LinkedInSummaryResponse)
def generate_linkedin_summary(
    resume_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume, _ = get_resume_and_job(resume_id, None, current_user, db)
    return AIService.generate_linkedin_summary(resume.raw_text or "", current_user.api_key_preference)


@router.post("/{resume_id}/rewrite", response_model=RewriteSectionResponse)
def generate_rewrite(
    resume_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume, _ = get_resume_and_job(resume_id, None, current_user, db)
    return AIService.generate_rewrite(resume.raw_text or "", current_user.api_key_preference)


@router.post("/{resume_id}/career-roadmap", response_model=RoadmapResponse)
def generate_career_roadmap(
    resume_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume, _ = get_resume_and_job(resume_id, None, current_user, db)
    return AIService.generate_career_roadmap(resume.raw_text or "", current_user.api_key_preference)


@router.post("/{resume_id}/chat", response_model=ChatMessageOut)
def chat_assistant(
    resume_id: int, 
    payload: ChatRequest,
    job_description_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume, job_text = get_resume_and_job(resume_id, job_description_id, current_user, db)
    
    # Fetch previous chat history
    history = db.query(ChatHistory).filter(
        ChatHistory.resume_id == resume_id,
        ChatHistory.user_id == current_user.id
    ).order_by(ChatHistory.created_at.asc()).all()
    
    history_dicts = [{"role": h.role, "content": h.content} for h in history]
    
    # Call AI
    response_text = AIService.chat_assistant(
        resume_text=resume.raw_text or "",
        chat_history=history_dicts,
        new_message=payload.message,
        job_desc_text=job_text,
        user_api_key=current_user.api_key_preference
    )
    
    # Save user message
    user_msg = ChatHistory(resume_id=resume.id, user_id=current_user.id, role="user", content=payload.message)
    db.add(user_msg)
    
    # Save assistant message
    asst_msg = ChatHistory(resume_id=resume.id, user_id=current_user.id, role="assistant", content=response_text)
    db.add(asst_msg)
    db.commit()
    db.refresh(asst_msg)
    
    return asst_msg


@router.get("/{resume_id}/chat", response_model=List[ChatMessageOut])
def get_chat_history(
    resume_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history = db.query(ChatHistory).filter(
        ChatHistory.resume_id == resume_id,
        ChatHistory.user_id == current_user.id
    ).order_by(ChatHistory.created_at.asc()).all()
    
    return history
