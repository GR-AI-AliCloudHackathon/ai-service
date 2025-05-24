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
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
    
    # Risk Thresholds
    LOW_RISK_THRESHOLD = int(os.getenv("LOW_RISK_THRESHOLD", "39"))
    MEDIUM_RISK_THRESHOLD = int(os.getenv("MEDIUM_RISK_THRESHOLD", "69"))
    
    # Audio Settings
    AUDIO_TEMP_DIR = "temp_audio"
    
settings = Settings()