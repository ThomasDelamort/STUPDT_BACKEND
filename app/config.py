from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres@localhost:5432/stupdt_db"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    # Groq API
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-20b"

    # Gemini API (fallback / alternative)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    @property
    def clean_groq_model(self) -> str:
        return self.GROQ_MODEL.split(" - ")[0].strip() or "openai/gpt-oss-20b"

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
