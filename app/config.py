# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Alibaba Cloud
    ALIBABA_ACCESS_KEY_ID = os.getenv("ALIBABA_ACCESS_KEY_ID")
    ALIBABA_ACCESS_KEY_SECRET = os.getenv("ALIBABA_ACCESS_KEY_SECRET")
    ALIBABA_REGION = os.getenv("ALIBABA_REGION", "ap-southeast-1")
    ALIBABA_APPKEY = os.getenv("ALIBABA_APPKEY")
    
    # Qwen LLM
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    
    # Database - ApsaraDB PostgreSQL
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://username:password@host:port/database")
    DATABASE_HOST = os.getenv("DATABASE_HOST")
    DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    DATABASE_USER = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DATABASE_SSL_MODE = os.getenv("DATABASE_SSL_MODE", "require")
    
    # Application Settings
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Risk Thresholds
    LOW_RISK_THRESHOLD = int(os.getenv("LOW_RISK_THRESHOLD", "39"))
    MEDIUM_RISK_THRESHOLD = int(os.getenv("MEDIUM_RISK_THRESHOLD", "69"))
    
    # Audio Settings
    AUDIO_TEMP_DIR = "temp_audio"
    MAX_AUDIO_SIZE_MB = int(os.getenv("MAX_AUDIO_SIZE_MB", "50"))
    
    @property
    def database_url(self) -> str:
        """Construct database URL if individual components are provided"""
        if self.DATABASE_URL and not self.DATABASE_URL.startswith("postgresql+asyncpg://username"):
            return self.DATABASE_URL
        
        if all([self.DATABASE_HOST, self.DATABASE_NAME, self.DATABASE_USER, self.DATABASE_PASSWORD]):
            return (
                f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
                f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
                f"?sslmode={self.DATABASE_SSL_MODE}"
            )
        
        raise ValueError("Database configuration is incomplete")
    
settings = Settings()