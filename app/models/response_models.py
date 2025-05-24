# app/models/response_models.py (UPDATE)
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

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

class ThreatIndicator(BaseModel):
    type: str
    severity: str
    timestamp_estimate: Optional[str] = None
    description: str
    confidence: float

class EvidenceDetails(BaseModel):
    full_transcript: str
    audio_duration_seconds: float
    processing_timestamp: str
    threat_indicators: List[ThreatIndicator]
    risk_assessment: Dict[str, Any]
    
class IncidentClassification(BaseModel):
    primary_category: str
    secondary_categories: List[str]
    severity_level: str
    urgency: str
    requires_immediate_action: bool

class SummaryResponse(BaseModel):
    # Evidence Kit Header
    evidence_kit_id: str
    incident_id: Optional[str] = None
    processing_timestamp: str
    
    # Basic Info
    ride_details: Dict[str, Any]
    audio_analysis: Dict[str, Any]
    
    # Main Summary
    executive_summary: str
    incident_classification: IncidentClassification
    
    # Detailed Evidence
    evidence_details: EvidenceDetails
    
    # Recommendations
    recommended_actions: List[str]
    follow_up_required: bool
    
    # Statistics
    overall_risk_score: float
    confidence_level: float