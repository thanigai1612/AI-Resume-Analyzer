from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/api/health", tags=["System Health"])

@router.get("")
def health_check():
    """
    Check system health and basic config presence.
    """
    status = {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "gemini_configured": bool(settings.GEMINI_API_KEY and "your_gemini" not in settings.GEMINI_API_KEY),
        "openai_configured": bool(settings.OPENAI_API_KEY and "your_openai" not in settings.OPENAI_API_KEY)
    }
    return status
