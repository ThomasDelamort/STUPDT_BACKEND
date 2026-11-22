import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.middleware.security import SecurityMiddleware
from app.routers import (
    health_router,
    chat_router,
    bureaucracy_router,
    telemetry_router,
    gemini_router,
    content_router,
    captcha_router,
    vision_router,
    apology_router
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="StuPDT Bureaucracy API",
    description="High-performance satirical backend with enterprise security defense",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(SecurityMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server exception on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal Bureaucracy Malfunction: The server encountered a catastrophic lack of enthusiasm.",
            "blame": "Server Emotional Instability",
            "code": "ERR_BUREAUCRATIC_EXCEPTION"
        }
    )


app.include_router(health_router)
app.include_router(chat_router)
app.include_router(bureaucracy_router)
app.include_router(telemetry_router)
app.include_router(gemini_router)
app.include_router(content_router)
app.include_router(captcha_router)
app.include_router(vision_router)
app.include_router(apology_router)
