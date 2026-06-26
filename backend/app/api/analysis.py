import csv
import json
from io import StringIO, BytesIO
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.models import Analysis, Resume, JobDescription, User
from app.schemas.analysis import AnalysisRequest, AnalysisOut, ComparisonRequest, ComparisonResponse, ComparisonResult
from app.core.dependencies import get_current_user
from app.services.ai_service import AIService
from app.services.pdf_generator import generate_pdf_report

router = APIRouter(prefix="/api/analysis", tags=["Resume Analysis"])

@router.post("/analyze", response_model=AnalysisOut, status_code=status.HTTP_201_CREATED)
def analyze_resume(
    payload: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify resume belongs to user
    resume = db.query(Resume).filter(Resume.id == payload.resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")

    job_title = "General Position"
    job_text = ""
    
    # Extract job description if provided
    if payload.job_description_id:
        job_desc = db.query(JobDescription).filter(
            JobDescription.id == payload.job_description_id, 
            JobDescription.user_id == current_user.id
        ).first()
        if not job_desc:
            raise HTTPException(status_code=404, detail="Saved Job Description not found")
        job_text = job_desc.description_text
        job_title = job_desc.title
    elif payload.job_description_text:
        job_text = payload.job_description_text
        job_title = "Custom Job Description"

    # Call AI Service
    # Use user api key if they configured it, otherwise system default
    user_api_key = current_user.api_key_preference
    try:
        analysis_data = AIService.analyze_resume(
            resume_text=resume.raw_text or "",
            job_desc_text=job_text,
            user_api_key=user_api_key
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Analysis Service failed: {str(e)}"
        )

    # Save to database
    db_analysis = Analysis(
        resume_id=resume.id,
        job_description_id=payload.job_description_id,
        analysis_results=analysis_data
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    return db_analysis


@router.get("/history", response_model=List[AnalysisOut])
def get_analysis_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated historical analyses for user.
    """
    history = db.query(Analysis).join(Resume).filter(
        Resume.user_id == current_user.id
    ).order_by(
        Analysis.created_at.desc()
    ).limit(limit).offset(offset).all()
    
    return history


@router.get("/{analysis_id}", response_model=AnalysisOut)
def get_analysis_detail(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    analysis = db.query(Analysis).join(Resume).filter(
        Analysis.id == analysis_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis report not found")
        
    return analysis


@router.delete("/{analysis_id}", status_code=status.HTTP_200_OK)
def delete_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    analysis = db.query(Analysis).join(Resume).filter(
        Analysis.id == analysis_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis report not found")
        
    db.delete(analysis)
    db.commit()
    return {"message": "Analysis history deleted successfully"}


@router.get("/{analysis_id}/export")
def export_analysis_report(
    analysis_id: int,
    export_format: str = Query("pdf", regex="^(pdf|json|csv)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    analysis = db.query(Analysis).join(Resume).filter(
        Analysis.id == analysis_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis report not found")
        
    resume_name = analysis.resume.filename
    results = analysis.analysis_results

    if export_format == "pdf":
        try:
            pdf_bytes = generate_pdf_report(resume_name, results)
            return StreamingResponse(
                BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=Analysis_Report_{resume_name}.pdf"}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate PDF document: {str(e)}"
            )

    elif export_format == "json":
        json_data = json.dumps(results, indent=2)
        return StreamingResponse(
            StringIO(json_data),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=Analysis_{resume_name}.json"}
        )

    elif export_format == "csv":
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        
        # Write general metrics
        writer.writerow(["Metric", "Value"])
        writer.writerow(["ATS Score", results.get("ats_score", 0)])
        writer.writerow(["Job Match Percentage", results.get("match_percentage", 0)])
        writer.writerow(["Experience Summary", results.get("experience_summary", "")])
        writer.writerow(["Education Summary", results.get("education_summary", "")])
        
        # Write skills
        writer.writerow([])
        writer.writerow(["Skills Detected"])
        for s in results.get("skills_detected", []):
            writer.writerow([s])
            
        writer.writerow([])
        writer.writerow(["Missing Skills"])
        for s in results.get("missing_skills", []):
            writer.writerow([s])
            
        writer.writerow([])
        writer.writerow(["Strengths"])
        for s in results.get("strengths", []):
            writer.writerow([s])
            
        writer.writerow([])
        writer.writerow(["Weaknesses"])
        for w in results.get("weaknesses", []):
            writer.writerow([w])

        csv_buffer.seek(0)
        return StreamingResponse(
            StringIO(csv_buffer.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=Analysis_{resume_name}.csv"}
        )


@router.post("/compare", response_model=ComparisonResponse)
def compare_resumes(
    payload: ComparisonRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compare multiple resumes side-by-side.
    """
    if len(payload.resume_ids) < 2:
        raise HTTPException(
            status_code=400, 
            detail="Provide at least 2 resume IDs for comparison"
        )
        
    resumes = db.query(Resume).filter(
        Resume.id.in_(payload.resume_ids), 
        Resume.user_id == current_user.id
    ).all()
    
    if len(resumes) != len(payload.resume_ids):
        raise HTTPException(
            status_code=404, 
            detail="One or more resumes were not found or access was denied"
        )

    comparisons = []
    all_skills_set = set()
    common_skills_set = None

    for resume in resumes:
        # Check if there is an existing analysis for this resume
        # If not, run a quick general analysis to seed comparison metrics
        latest_analysis = db.query(Analysis).filter(
            Analysis.resume_id == resume.id
        ).order_by(Analysis.created_at.desc()).first()

        if latest_analysis:
            results = latest_analysis.analysis_results
        else:
            # Generate a default analysis on the fly
            results = AIService.analyze_resume(
                resume_text=resume.raw_text or "",
                job_desc_text=payload.job_description_text,
                user_api_key=current_user.api_key_preference
            )
            # Save it
            latest_analysis = Analysis(
                resume_id=resume.id,
                analysis_results=results
            )
            db.add(latest_analysis)
            db.commit()
            db.refresh(latest_analysis)

        skills = results.get("skills_detected", [])
        all_skills_set.update(skills)
        
        if common_skills_set is None:
            common_skills_set = set(skills)
        else:
            common_skills_set.intersection_update(skills)

        comparisons.append(ComparisonResult(
            resume_id=resume.id,
            filename=resume.filename,
            ats_score=results.get("ats_score", 0),
            match_percentage=results.get("match_percentage", 0),
            skills_detected=skills,
            missing_skills=results.get("missing_skills", []),
            strengths=results.get("strengths", [])[:3],
            weaknesses=results.get("weaknesses", [])[:3]
        ))

    return ComparisonResponse(
        comparisons=comparisons,
        common_skills=list(common_skills_set or set()),
        all_skills=list(all_skills_set)
    )
