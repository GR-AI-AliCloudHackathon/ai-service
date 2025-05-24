# app/database/repositories.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from .models import (
    Driver, Passenger, Ride, AudioAssessment, ThreatIndicator, 
    Incident, LocationRisk, SystemLog, RiskLevelEnum
)

class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

class DriverRepository(BaseRepository):
    async def create_driver(self, driver_data: Dict[str, Any]) -> Driver:
        driver = Driver(**driver_data)
        self.session.add(driver)
        await self.session.flush()
        return driver
    
    async def get_driver_by_id(self, driver_id: str) -> Optional[Driver]:
        stmt = select(Driver).where(Driver.driver_id == driver_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_driver_risk_score(self, driver_id: str, new_score: float):
        stmt = update(Driver).where(Driver.driver_id == driver_id).values(
            risk_history_score=new_score,
            updated_at=datetime.utcnow()
        )
        await self.session.execute(stmt)

class AudioAssessmentRepository(BaseRepository):
    async def create_assessment(self, assessment_data: Dict[str, Any]) -> AudioAssessment:
        assessment = AudioAssessment(**assessment_data)
        self.session.add(assessment)
        await self.session.flush()
        return assessment
    
    async def get_assessment_by_id(self, assessment_id: str) -> Optional[AudioAssessment]:
        stmt = select(AudioAssessment).where(AudioAssessment.assessment_id == assessment_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_assessments_by_driver(self, driver_id: str, limit: int = 50) -> List[AudioAssessment]:
        stmt = (select(AudioAssessment)
                .where(AudioAssessment.driver_id == driver_id)
                .order_by(AudioAssessment.created_at.desc())
                .limit(limit))
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_high_risk_assessments(self, hours: int = 24) -> List[AudioAssessment]:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        stmt = (select(AudioAssessment)
                .where(and_(
                    AudioAssessment.risk_level == RiskLevelEnum.HIGH,
                    AudioAssessment.created_at >= cutoff_time
                ))
                .order_by(AudioAssessment.created_at.desc()))
        result = await self.session.execute(stmt)
        return result.scalars().all()

class ThreatIndicatorRepository(BaseRepository):
    async def create_threat_indicators(self, indicators_data: List[Dict[str, Any]]) -> List[ThreatIndicator]:
        indicators = [ThreatIndicator(**data) for data in indicators_data]
        self.session.add_all(indicators)
        await self.session.flush()
        return indicators
    
    async def get_threats_by_assessment(self, assessment_id: str) -> List[ThreatIndicator]:
        stmt = select(ThreatIndicator).where(ThreatIndicator.assessment_id == assessment_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

class IncidentRepository(BaseRepository):
    async def create_incident(self, incident_data: Dict[str, Any]) -> Incident:
        incident = Incident(**incident_data)
        self.session.add(incident)
        await self.session.flush()
        return incident
    
    async def get_incident_by_id(self, incident_id: str) -> Optional[Incident]:
        stmt = select(Incident).where(Incident.incident_id == incident_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_open_incidents(self) -> List[Incident]:
        stmt = (select(Incident)
                .where(Incident.status.in_(["open", "investigating"]))
                .order_by(Incident.created_at.desc()))
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def update_incident_status(self, incident_id: str, status: str, notes: str = None):
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        if notes:
            update_data["resolution_notes"] = notes
        if status == "resolved":
            update_data["resolved_at"] = datetime.utcnow()
            
        stmt = update(Incident).where(Incident.incident_id == incident_id).values(**update_data)
        await self.session.execute(stmt)

class LocationRiskRepository(BaseRepository):
    async def get_location_risk(self, lat: float, lng: float, radius_km: float = 1.0) -> Optional[LocationRisk]:
        # Simple distance calculation - in production, use PostGIS for better performance
        stmt = select(LocationRisk).where(
            and_(
                func.abs(LocationRisk.latitude - lat) < radius_km / 111.0,  # Rough conversion
                func.abs(LocationRisk.longitude - lng) < radius_km / 111.0
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_location_risk(self, lat: float, lng: float, risk_index: float):
        # Check if location exists
        location = await self.get_location_risk(lat, lng)
        
        if location:
            stmt = update(LocationRisk).where(LocationRisk.id == location.id).values(
                risk_index=risk_index,
                incident_count=LocationRisk.incident_count + 1,
                last_updated=datetime.utcnow()
            )
            await self.session.execute(stmt)
        else:
            # Create new location risk entry
            location_risk = LocationRisk(
                latitude=lat,
                longitude=lng,
                risk_index=risk_index,
                incident_count=1
            )
            self.session.add(location_risk)

class SystemLogRepository(BaseRepository):
    async def log(self, level: str, service: str, message: str, context: Dict[str, Any] = None):
        log_entry = SystemLog(
            log_level=level,
            service=service,
            message=message,
            context=context
        )
        self.session.add(log_entry)
        await self.session.flush()
    
    async def get_recent_logs(self, hours: int = 24, level: str = None) -> List[SystemLog]:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        stmt = select(SystemLog).where(SystemLog.created_at >= cutoff_time)
        
        if level:
            stmt = stmt.where(SystemLog.log_level == level)
            
        stmt = stmt.order_by(SystemLog.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

# Repository factory
class RepositoryManager:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.drivers = DriverRepository(session)
        self.assessments = AudioAssessmentRepository(session)
        self.threats = ThreatIndicatorRepository(session)
        self.incidents = IncidentRepository(session)
        self.locations = LocationRiskRepository(session)
        self.logs = SystemLogRepository(session)
