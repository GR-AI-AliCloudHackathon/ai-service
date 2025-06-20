# app/models/request_models.py (UPDATE)
from pydantic import BaseModel
from typing import Optional

class AudioAssessmentRequest(BaseModel):
    # Audio file will be uploaded via form data
    driver_id: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    route_expected: Optional[str] = None

class SummarizerRequest(BaseModel):
    # Audio file will be uploaded via form data
    incident_id: Optional[str] = None
    ride_id: Optional[str] = None
    passenger_id: Optional[str] = None
    driver_id: Optional[str] = None
    additional_context: Optional[str] = None