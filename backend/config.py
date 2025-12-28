# backend/config.py
from pydantic import BaseModel
import os


class Settings(BaseModel):
    APP_NAME: str = "API Copilot Backend"
    ENV: str = "dev"

    # API
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Auth (later)
    JWT_SECRET: str = "dev-secret"
    JWT_ALGORITHM: str = "HS256"

    # Database (later)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/api_copilot"

    # LLM (later)
    GEMINI_API_KEY: str | None = None


def load_settings() -> Settings:
    return Settings(
        APP_NAME=os.getenv("APP_NAME", "API Copilot Backend"),
        ENV=os.getenv("ENV", "dev"),
        JWT_SECRET=os.getenv("JWT_SECRET", "dev-secret"),
        DATABASE_URL=os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/api_copilot"
           ),
        GEMINI_API_KEY=os.getenv("GEMINI_API_KEY"),
    )


settings = load_settings()
