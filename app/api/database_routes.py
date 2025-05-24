# app/api/database_routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from ..database.database import get_db
from ..services.database_service import DatabaseService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/db", tags=["database"])

@router.get("/assessments/recent")
async def get_recent_assessments(
    hours: int = Query(24, description="Hours to look back"),
    db: AsyncSession = Depends(get_db)
):
    """Get recent high-risk assessments"""
    db_service = DatabaseService(db)
    assessments = await db_service.get_recent_high_risk_assessments(hours)
    return {"assessments": assessments, "count": len(assessments)}

@router.get("/assessment/{assessment_id}")
async def get_assessment_details(
    assessment_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed assessment information"""
    db_service = DatabaseService(db)
    assessment = await db_service.get_assessment_by_id(assessment_id)
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return assessment

@router.get("/driver/{driver_id}/risk")
async def get_driver_risk(
    driver_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get driver risk score and history"""
    db_service = DatabaseService(db)
    risk_score = await db_service.get_driver_risk_history(driver_id)
    return {"driver_id": driver_id, "risk_score": risk_score}

@router.get("/location/risk")
async def get_location_risk(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    db: AsyncSession = Depends(get_db)
):
    """Get risk index for a location"""
    db_service = DatabaseService(db)
    risk_index = await db_service.get_location_risk_index(lat, lng)
    return {"location": {"lat": lat, "lng": lng}, "risk_index": risk_index}

@router.get("/health/database")
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """Check database health and connectivity"""
    try:
        # Simple query to test connection
        await db.execute("SELECT 1")
        return {
            "status": "healthy",
            "message": "Database connection is working"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")
