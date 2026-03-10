import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Nexus API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/v1"
    
    # Security
    API_KEY_NAME: str = "X-Nexus-Key"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/nexus")

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Fixes postgres:// vs postgresql:// for SQLAlchemy 2.0+"""
        url = self.DATABASE_URL
        if url and url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql://", 1)
        return url

    class Config:
        case_sensitive = True

settings = Settings()
