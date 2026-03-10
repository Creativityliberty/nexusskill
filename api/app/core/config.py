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

    class Config:
        case_sensitive = True

settings = Settings()
