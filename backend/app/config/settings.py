"""
Configuration Settings for SentinelOps-Nexus
Loads environment variables and provides app configuration
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "SentinelOps-Nexus"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "sentinelops_nexus"
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-this-in-production-power-rangers-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # QR Token Settings
    QR_TOKEN_LENGTH: int = 32
    
    # Default Admin Credentials (for first setup)
    DEFAULT_ADMIN_USERNAME: str = "red_ranger"
    DEFAULT_ADMIN_PASSWORD: str = "morphintime2024"
    DEFAULT_ADMIN_FULLNAME: str = "Red Ranger - Team Leader"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()