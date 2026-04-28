"""Application configuration module."""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized strongly-typed settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"

    APP_NAME: str = "PDF MCQ Generator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    FRONTEND_URL: str = "https://msq-smoky.vercel.app"
    BACKEND_URL: str = "http://localhost:8000"
    
    # Allow multiple frontend URLs (comma-separated for production)
    # Supports both Vercel production URL and localhost for development
    FRONTEND_URLS: str = "http://localhost:3000,http://localhost:5173"

    MAX_FILE_SIZE: int = 50
    ALLOWED_EXTENSIONS: str = "pdf"

    CHROMA_DB_PATH: str = "./chroma_db"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100

    DEFAULT_NUM_QUESTIONS: int = 10
    DEFAULT_DIFFICULTY: str = "medium"
    MAX_QUESTIONS_PER_REQUEST: int = 20
    
    # Cleanup settings
    CLEANUP_ENABLED: bool = True
    CLEANUP_MAX_AGE_HOURS: int = 24  # Delete files/collections older than 24 hours

    @property
    def allowed_extensions(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",") if ext.strip()]


settings = Settings()

