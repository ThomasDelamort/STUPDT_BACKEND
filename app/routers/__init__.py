from app.routers.health import router as health_router
from app.routers.chat import router as chat_router
from app.routers.bureaucracy import router as bureaucracy_router
from app.routers.telemetry import router as telemetry_router
from app.routers.gemini import router as gemini_router
from app.routers.content import router as content_router
from app.routers.captcha import router as captcha_router
from app.routers.vision import router as vision_router
from app.routers.apology import router as apology_router

__all__ = [
    "health_router",
    "chat_router",
    "bureaucracy_router",
    "telemetry_router",
    "gemini_router",
    "content_router",
    "captcha_router",
    "vision_router",
    "apology_router"
]
