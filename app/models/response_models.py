# app/models/response_models.py
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium" 
    HIGH = "High"

class AssessmentResponse(BaseModel):
    risk_score: float
    risk_level: RiskLevel
    threat_text_score: float
    location_risk_index: float
    driver_history_score: float
    transcribed_text: str
    action_required: bool
    push_notification: Optional[str] = None

class SummaryResponse(BaseModel):
    session_id: str
    incident_summary: str
    total_risk_events: int
    highest_risk_score: float
    duration_minutes: float