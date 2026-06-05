"""Konfigurasi aplikasi CV Recommender API."""
import os


class Settings:
    """Application settings loaded from environment variables."""

    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8080"))
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000"
    ).split(",")

    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    TOP_K_DEFAULT: int = int(os.getenv("TOP_K_DEFAULT", "5"))

    MODEL_DIR: str = os.getenv("MODEL_DIR", "models")


settings = Settings()
