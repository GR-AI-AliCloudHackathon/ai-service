# app/services/database_service.py
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging

from ..database.repositories import RepositoryManager
from ..database.models import RiskLevelEnum, IncidentSeverityEnum, IncidentUrgencyEnum

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service layer for database operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = RepositoryManager(session)
    
    async def store_assessment(self, assessment_data: Dict[str, Any]) -> str:
        """Store audio assessment in database"""
        try:
            assessment = await self.repo.assessments.create_assessment(assessment_data)
            return assessment.assessment_id
        except Exception as e:
            logger.error(f"Error storing assessment: {e}")
            raise
    
    async def store_threat_indicators(self, assessment_id: str, indicators: List[Dict[str, Any]]):
        """Store threat indicators for an assessment"""
        try:
            # Add assessment_id to each indicator
            for indicator in indicators:
                indicator["assessment_id"] = assessment_id
            
            await self.repo.threats.create_threat_indicators(indicators)
        except Exception as e:
            logger.error(f"Error storing threat indicators: {e}")
            raise
    
    async def create_incident(self, incident_data: Dict[str, Any]) -> str:
        """Create a new incident record"""
        try:
            incident = await self.repo.incidents.create_incident(incident_data)
            
            # Log incident creation
            await self.repo.logs.log(
                level="WARNING",
                service="incident_creation",
                message=f"New incident created: {incident.incident_id}",
                context={
                    "incident_id": incident.incident_id,
                    "severity": incident.severity_level.value,
                    "driver_id": incident.driver_id
                }
            )
            
            return incident.incident_id
        except Exception as e:
            logger.error(f"Error creating incident: {e}")
            raise
    
    async def get_driver_risk_history(self, driver_id: str) -> float:
        """Get driver's risk history score"""
        try:
            driver = await self.repo.drivers.get_driver_by_id(driver_id)
            if driver:
                return driver.risk_history_score
            else:
                # Create new driver record
                driver_data = {
                    "driver_id": driver_id,
                    "risk_history_score": 0.0
                }
                await self.repo.drivers.create_driver(driver_data)
                return 0.0
        except Exception as e:
            logger.error(f"Error getting driver risk history: {e}")
            return 0.0
    
    async def update_driver_risk_score(self, driver_id: str, new_score: float):
        """Update driver's risk score"""
        try:
            await self.repo.drivers.update_driver_risk_score(driver_id, new_score)
        except Exception as e:
            logger.error(f"Error updating driver risk score: {e}")
    
    async def get_location_risk_index(self, lat: float, lng: float) -> float:
        """Get risk index for a location"""
        try:
            location_risk = await self.repo.locations.get_location_risk(lat, lng)
            return location_risk.risk_index if location_risk else 0.0
        except Exception as e:
            logger.error(f"Error getting location risk: {e}")
            return 0.0
    
    async def update_location_risk(self, lat: float, lng: float, risk_index: float):
        """Update location risk index"""
        try:
            await self.repo.locations.update_location_risk(lat, lng, risk_index)
        except Exception as e:
            logger.error(f"Error updating location risk: {e}")
    
    async def get_recent_high_risk_assessments(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent high-risk assessments for monitoring"""
        try:
            assessments = await self.repo.assessments.get_high_risk_assessments(hours)
            return [
                {
                    "assessment_id": a.assessment_id,
                    "driver_id": a.driver_id,
                    "risk_score": a.risk_score,
                    "risk_level": a.risk_level.value,
                    "location": {"lat": a.location_lat, "lng": a.location_lng},
                    "created_at": a.created_at.isoformat()
                }
                for a in assessments
            ]
        except Exception as e:
            logger.error(f"Error getting high-risk assessments: {e}")
            return []
    
    async def log_system_event(self, level: str, service: str, message: str, context: Dict[str, Any] = None):
        """Log system events"""
        try:
            await self.repo.logs.log(level, service, message, context)
        except Exception as e:
            logger.error(f"Error logging system event: {e}")
    
    async def get_assessment_by_id(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Get assessment details by ID"""
        try:
            assessment = await self.repo.assessments.get_assessment_by_id(assessment_id)
            if not assessment:
                return None
            
            # Get associated threat indicators
            threats = await self.repo.threats.get_threats_by_assessment(assessment_id)
            
            return {
                "assessment_id": assessment.assessment_id,
                "driver_id": assessment.driver_id,
                "risk_score": assessment.risk_score,
                "risk_level": assessment.risk_level.value,
                "transcribed_text": assessment.transcribed_text,
                "location": {"lat": assessment.location_lat, "lng": assessment.location_lng},
                "threat_indicators": [
                    {
                        "type": t.type,
                        "severity": t.severity,
                        "description": t.description,
                        "confidence": t.confidence
                    }
                    for t in threats
                ],
                "created_at": assessment.created_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting assessment: {e}")
            return None
