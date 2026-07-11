from __future__ import annotations

import os


class Config:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # Database
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL", "sqlite:///compass_ai.sqlite3"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # AI
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai_compatible")
    AI_BASE_URL: str = os.getenv("AI_BASE_URL", "")
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4o-mini")

    # Rate limiting (simple in-app)
    AI_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "30"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
