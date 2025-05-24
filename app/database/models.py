# app/database/models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum

Base = declarative_base()

class RiskLevelEnum(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class IncidentSeverityEnum(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class IncidentUrgencyEnum(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    IMMEDIATE = "Immediate"

class Driver(Base):
    __tablename__ = "drivers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255))
    phone = Column(String(20))
    email = Column(String(255))
    license_number = Column(String(100))
    risk_history_score = Column(Float, default=0.0)
    total_rides = Column(Integer, default=0)
    incident_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Passenger(Base):
    __tablename__ = "passengers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    passenger_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255))
    phone = Column(String(20))
    email = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Ride(Base):
    __tablename__ = "rides"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ride_id = Column(String(100), unique=True, index=True, nullable=False)
    driver_id = Column(String(100), nullable=False, index=True)
    passenger_id = Column(String(100), nullable=False, index=True)
    pickup_location = Column(JSON)  # {"lat": float, "lng": float, "address": str}
    destination_location = Column(JSON)
    route_expected = Column(Text)
    ride_start_time = Column(DateTime)
    ride_end_time = Column(DateTime)
    status = Column(String(50), default="active")  # active, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AudioAssessment(Base):
    __tablename__ = "audio_assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(String(100), unique=True, index=True, nullable=False)
    driver_id = Column(String(100), nullable=False, index=True)
    ride_id = Column(String(100), index=True)
    
    # Audio file info
    audio_file_path = Column(String(500))
    audio_duration_seconds = Column(Float)
    audio_format = Column(String(10))
    
    # Location data
    location_lat = Column(Float)
    location_lng = Column(Float)
    route_expected = Column(Text)
    
    # Transcription
    transcribed_text = Column(Text)
    transcription_confidence = Column(Float)
    
    # Risk assessment
    risk_score = Column(Float, nullable=False)
    risk_level = Column(Enum(RiskLevelEnum), nullable=False)
    threat_text_score = Column(Float)
    location_risk_index = Column(Float)
    driver_history_score = Column(Float)
    
    # Actions
    action_required = Column(Boolean, default=False)
    push_notification = Column(Text)
    
    # Metadata
    processing_timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class ThreatIndicator(Base):
    __tablename__ = "threat_indicators"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(String(100), nullable=False, index=True)
    
    type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    timestamp_estimate = Column(String(100))
    description = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(String(100), unique=True, index=True, nullable=False)
    evidence_kit_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Related entities
    ride_id = Column(String(100), index=True)
    passenger_id = Column(String(100), index=True)
    driver_id = Column(String(100), nullable=False, index=True)
    assessment_id = Column(String(100), index=True)
    
    # Audio analysis
    audio_file_path = Column(String(500))
    audio_duration_seconds = Column(Float)
    full_transcript = Column(Text)
    
    # Classification
    primary_category = Column(String(100), nullable=False)
    secondary_categories = Column(JSON)  # List of strings
    severity_level = Column(Enum(IncidentSeverityEnum), nullable=False)
    urgency = Column(Enum(IncidentUrgencyEnum), nullable=False)
    requires_immediate_action = Column(Boolean, default=False)
    
    # Summary and analysis
    executive_summary = Column(Text, nullable=False)
    risk_assessment = Column(JSON)
    recommended_actions = Column(JSON)  # List of strings
    follow_up_required = Column(Boolean, default=False)
    
    # Statistics
    overall_risk_score = Column(Float, nullable=False)
    confidence_level = Column(Float, nullable=False)
    
    # Metadata
    processing_timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status tracking
    status = Column(String(50), default="open")  # open, investigating, resolved, closed
    assigned_to = Column(String(255))
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime)

class LocationRisk(Base):
    __tablename__ = "location_risks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_name = Column(String(255))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    risk_index = Column(Float, nullable=False, default=0.0)
    risk_factors = Column(JSON)  # List of risk factors
    incident_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Geographic indexing
    geohash = Column(String(20), index=True)  # For efficient geographic queries

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    log_level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, CRITICAL
    service = Column(String(100), nullable=False)  # speech_service, qwen_service, etc.
    message = Column(Text, nullable=False)
    context = Column(JSON)  # Additional context data
    user_id = Column(String(100))
    session_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
