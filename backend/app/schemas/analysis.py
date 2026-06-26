from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class KeywordItem(BaseModel):
    word: str
    count: int
    density: float
    status: str  # "Good" | "Missing" | "Overused"

class ContactValidation(BaseModel):
    email: bool
    phone: bool
    linkedin: bool
    portfolio: bool
    suggestions: List[str]

class GrammarIssue(BaseModel):
    issue: str
    suggestion: str
    snippet: str

class ResumeLengthAnalysis(BaseModel):
    length_type: str  # "Too Short" | "Ideal" | "Too Long"
    word_count: int
    page_count: int
    advice: str

class ActionVerbAnalysis(BaseModel):
    count: int
    verbs: List[str]
    rating: str  # "Weak" | "Moderate" | "Strong"
    advice: str

class AIAnalysisResult(BaseModel):
    ats_score: int = Field(..., ge=0, le=100)
    match_percentage: int = Field(..., ge=0, le=100)
    skills_detected: List[str]
    missing_skills: List[str]
    technical_skills: List[str]
    soft_skills: List[str]
    keyword_analysis: List[KeywordItem]
    experience_summary: str
    education_summary: str
    certifications: List[str]
    projects: List[str]
    contact_validation: ContactValidation
    grammar_check: List[GrammarIssue]
    formatting_suggestions: List[str]
    resume_length_analysis: ResumeLengthAnalysis
    action_verb_analysis: ActionVerbAnalysis
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]
    recruiter_tips: List[str]

class AnalysisRequest(BaseModel):
    resume_id: int
    job_description_id: Optional[int] = None
    job_description_text: Optional[str] = None

class AnalysisOut(BaseModel):
    id: int
    resume_id: int
    job_description_id: Optional[int]
    analysis_results: Dict  # Use dict here for flexible ORM serialization
    created_at: datetime

    class Config:
        from_attributes = True

class ComparisonRequest(BaseModel):
    resume_ids: List[int]
    job_description_id: Optional[int] = None
    job_description_text: Optional[str] = None

class ComparisonResult(BaseModel):
    resume_id: int
    filename: str
    ats_score: int
    match_percentage: int
    skills_detected: List[str]
    missing_skills: List[str]
    strengths: List[str]
    weaknesses: List[str]

class ComparisonResponse(BaseModel):
    comparisons: List[ComparisonResult]
    common_skills: List[str]
    all_skills: List[str]
