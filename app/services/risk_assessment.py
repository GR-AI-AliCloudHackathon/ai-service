# app/services/risk_assessment.py
import logging
from typing import Tuple
from app.config import settings
from app.models.response_models import RiskLevel

logger = logging.getLogger(__name__)

class RiskAssessmentService:
    
    def calculate_location_risk(self, lat: float = None, lng: float = None, 
                              expected_route: str = None) -> float:
        """
        Calculate location risk index
        For hackathon: using dummy values, but here's how to implement:
        
        Real implementation would consider:
        - Deviation from expected route (GPS tracking)
        - Known unsafe areas (crime database)
        - Time of day risk factors
        - Traffic/road conditions
        """
        # Dummy implementation for hackathon
        if lat is None or lng is None:
            return 10.0  # Default low risk
        
        # Simulate route deviation check
        # In real app: compare current location with expected route
        route_deviation_risk = 15.0  # 0-30 scale
        
        # Simulate area safety score
        # In real app: lookup crime statistics, lighting, population density
        area_safety_risk = 5.0  # 0-30 scale
        
        # Time-based risk (night time = higher risk)
        from datetime import datetime
        current_hour = datetime.now().hour
        time_risk = 20.0 if 22 <= current_hour or current_hour <= 5 else 5.0
        
        total_location_risk = min(40.0, route_deviation_risk + area_safety_risk + time_risk)
        return total_location_risk
    
    def get_driver_history_score(self, driver_id: str = None) -> float:
        """
        Get driver history risk score
        For hackathon: using dummy values
        
        Real implementation would query database for:
        - Previous incident reports
        - Customer complaints
        - Safety violations
        - Background check results
        """
        # Dummy implementation
        if driver_id is None:
            return 5.0  # Default good driver
        
        # Simulate database lookup
        dummy_driver_scores = {
            "good_driver": 0.0,
            "average_driver": 10.0,
            "concerning_driver": 25.0,
            "bad_driver": 40.0
        }
        
        # For demo, randomly assign based on driver_id hash
        score_key = ["good_driver", "average_driver", "concerning_driver"][
            hash(driver_id) % 3
        ]
        return dummy_driver_scores[score_key]
    
    def calculate_overall_risk(self, threat_text_score: float, 
                             location_risk: float, driver_history: float) -> Tuple[float, RiskLevel]:
        """
        Calculate overall risk score and determine risk level
        
        Weighting:
        - Threat text: 60% (most important indicator)
        - Location risk: 25%
        - Driver history: 15%
        """
        weights = {
            'threat': 0.6,
            'location': 0.25,
            'driver': 0.15
        }
        
        overall_score = (
            threat_text_score * weights['threat'] +
            location_risk * weights['location'] +
            driver_history * weights['driver']
        )
        
        # Determine risk level
        if overall_score <= settings.LOW_RISK_THRESHOLD:
            risk_level = RiskLevel.LOW
        elif overall_score <= settings.MEDIUM_RISK_THRESHOLD:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.HIGH
        
        return overall_score, risk_level
    
    def get_push_notification_message(self, risk_level: RiskLevel) -> str:
        """Generate appropriate push notification message"""
        messages = {
            RiskLevel.MEDIUM: "We see your risk is at medium level, help me to confirm this by giving yes/no",
            RiskLevel.HIGH: "We see your risk is at high level, help me to confirm this by giving yes/no"
        }
        return messages.get(risk_level, "")