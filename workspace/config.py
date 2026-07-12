from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # Database
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL", "sqlite:///compass_ai.sqlite3"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # AI
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai_compatible")

    # OpenAI-compatible (optional)
    AI_BASE_URL: str = os.getenv("AI_BASE_URL", "")
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4o-mini")

    # Azure OpenAI (optional)
    # Support both AZURE_* and legacy/alternate names.
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")

    # If the app is configured with OpenAI-compatible names, allow fallback.
    # (Not required for your current .env, but keeps the prototype flexible.)
    AI_BASE_URL: str = os.getenv("AI_BASE_URL", os.getenv("AZURE_OPENAI_ENDPOINT", ""))
    AI_API_KEY: str = os.getenv("AI_API_KEY", os.getenv("AZURE_OPENAI_API_KEY", ""))
    AI_MODEL: str = os.getenv("AI_MODEL", os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5-nano"))

    # Rate limiting (simple in-app)
    AI_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "30"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
