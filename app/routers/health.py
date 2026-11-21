from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check():
    ai_provider = "groq" if settings.GROQ_API_KEY else "gemini" if settings.GEMINI_API_KEY else "offline_fallbacks"
    active_model = settings.clean_groq_model if ai_provider == "groq" else settings.GEMINI_MODEL if ai_provider == "gemini" else "none"

    return {
        "status": "healthy",
        "online": True,
        "service": "StuPDT Backend",
        "database": "postgresql",
        "ai_provider": ai_provider,
        "model": active_model
    }
