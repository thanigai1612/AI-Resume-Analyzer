from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ResumeOut(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime
    text_length: int

    class Config:
        from_attributes = True

class ResumeDetailOut(BaseModel):
    id: int
    filename: str
    raw_text: Optional[str]
    uploaded_at: datetime

    class Config:
        from_attributes = True

class JobDescriptionCreate(BaseModel):
    title: str
    description_text: str

class JobDescriptionOut(BaseModel):
    id: int
    title: str
    description_text: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str

class ChatMessageOut(BaseModel):
    id: int
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class CoverLetterResponse(BaseModel):
    cover_letter: str

class InterviewQuestionsResponse(BaseModel):
    questions: List[dict]  # list of {"question": ..., "type": ..., "ideal_answer": ...}

class LinkedInSummaryResponse(BaseModel):
    linkedin_summary: str
    headline_suggestions: List[str]
    portfolio_summary: str

class RewriteSectionResponse(BaseModel):
    original_summary: str
    suggested_summary: str
    original_skills: List[str]
    suggested_skills: List[str]
    suggested_bullets: List[dict]  # list of {"original": ..., "improved": ..., "reason": ...}
    ats_friendly_markdown: str

class RoadmapResponse(BaseModel):
    career_path: str
    timeline_steps: List[dict]  # list of {"step": ..., "timeline": ..., "skills_to_acquire": ..., "resources": ...}
    industry: str
    career_level: str
    readability_score: int
    salary_estimate: str
