# app/services/qwen_service.py (UPDATE)
import json
import logging
from openai import OpenAI
from app.config import settings
from typing import Dict, List, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class QwenService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.DASHSCOPE_API_KEY,
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        )
    
    def assess_threat_level(self, transcribed_text: str) -> float:
        """Assess threat level from transcribed text using Qwen"""
        if not transcribed_text or len(transcribed_text.strip()) < 5:
            return 0.0
        
        prompt = f"""
        Analyze the following conversation transcript from a ride-sharing service for potential safety threats to passengers (especially women and children).
        
        Rate the threat level on a scale of 0-100 where:
        - 0-30: Normal conversation, no threats
        - 31-60: Concerning language, inappropriate comments, mild threats
        - 61-100: Serious threats, aggressive language, sexual harassment, violence indicators
        
        Consider these threat indicators:
        - Inappropriate sexual comments or advances
        - Threats of violence or harm
        - Aggressive or hostile language
        - Attempts to deviate from planned route
        - Requests for personal information
        - Drug/alcohol references affecting safety
        
        Transcript: "{transcribed_text}"
        
        Respond with only a JSON object: {{"threat_score": <number>, "reasoning": "<brief explanation>"}}
        """
        
        try:
            completion = self.client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": "You are a safety assessment AI focused on passenger protection in ride-sharing scenarios."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(completion.choices[0].message.content)
            threat_score = float(result.get("threat_score", 0))
            
            # Ensure score is within bounds
            return max(0, min(100, threat_score))
            
        except Exception as e:
            logger.error(f"Error in threat assessment: {e}")
            return 0.0
    
    def create_evidence_kit(self, transcript: str, audio_duration: float, 
                           risk_assessment: Dict[str, Any], 
                           ride_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create comprehensive evidence kit from audio transcript"""
        
        if not transcript or len(transcript.strip()) < 5:
            transcript = "[No clear speech detected in audio]"
        
        analysis_prompt = f"""
        You are a forensic analyst creating an evidence kit for a ride-sharing safety incident.
        
        Analyze this conversation transcript and create a comprehensive incident report.
        
        TRANSCRIPT: "{transcript}"
        AUDIO_DURATION: {audio_duration} seconds
        RISK_SCORE: {risk_assessment.get('overall_score', 0)}
        
        Create a detailed analysis in the following JSON structure:
        {{
            "executive_summary": "Brief 2-3 sentence summary of the incident",
            "incident_classification": {{
                "primary_category": "harassment|threat|inappropriate_conduct|route_deviation|other",
                "secondary_categories": ["list", "of", "relevant", "tags"],
                "severity_level": "low|medium|high|critical",
                "urgency": "immediate|high|medium|low",
                "requires_immediate_action": true/false
            }},
            "threat_indicators": [
                {{
                    "type": "verbal_threat|sexual_harassment|aggressive_behavior|route_deviation|other",
                    "severity": "low|medium|high|critical",
                    "timestamp_estimate": "approximate time if detectable",
                    "description": "specific description of the indicator",
                    "confidence": 0.0-1.0
                }}
            ],
            "detailed_analysis": {{
                "conversation_tone": "description of overall tone",
                "power_dynamics": "analysis of speaker dynamics",
                "escalation_pattern": "how situation developed",
                "safety_concerns": ["list", "of", "specific", "concerns"],
                "protective_factors": ["any", "positive", "safety", "elements"]
            }},
            "recommended_actions": [
                "immediate actions needed",
                "follow-up steps",
                "preventive measures"
            ],
            "follow_up_required": true/false,
            "confidence_level": 0.0-1.0,
            "additional_notes": "any other relevant observations"
        }}
        
        Focus on passenger safety, be objective, and provide actionable insights.
        If the transcript shows normal conversation, indicate that clearly.
        """
        
        try:
            completion = self.client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": "You are a professional forensic analyst specializing in ride-sharing safety incidents. Provide thorough, objective analysis."},
                    {"role": "user", "content": analysis_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            analysis_result = json.loads(completion.choices[0].message.content)
            
            # Create complete evidence kit
            evidence_kit = {
                "evidence_kit_id": str(uuid.uuid4()),
                "processing_timestamp": datetime.now().isoformat(),
                "ride_details": ride_context or {},
                "audio_analysis": {
                    "duration_seconds": audio_duration,
                    "transcript_length": len(transcript),
                    "speech_detected": len(transcript.strip()) > 10,
                    "processing_quality": "good" if len(transcript) > 50 else "limited"
                },
                "executive_summary": analysis_result.get("executive_summary", "No significant safety concerns detected."),
                "incident_classification": analysis_result.get("incident_classification", {
                    "primary_category": "normal_ride",
                    "secondary_categories": [],
                    "severity_level": "low",
                    "urgency": "low",
                    "requires_immediate_action": False
                }),
                "evidence_details": {
                    "full_transcript": transcript,
                    "audio_duration_seconds": audio_duration,
                    "processing_timestamp": datetime.now().isoformat(),
                    "threat_indicators": analysis_result.get("threat_indicators", []),
                    "risk_assessment": risk_assessment
                },
                "detailed_analysis": analysis_result.get("detailed_analysis", {}),
                "recommended_actions": analysis_result.get("recommended_actions", ["No specific actions required"]),
                "follow_up_required": analysis_result.get("follow_up_required", False),
                "overall_risk_score": risk_assessment.get('overall_score', 0),
                "confidence_level": analysis_result.get("confidence_level", 0.8)
            }
            
            return evidence_kit
            
        except Exception as e:
            logger.error(f"Error creating evidence kit: {e}")
            # Return basic evidence kit in case of error
            return {
                "evidence_kit_id": str(uuid.uuid4()),
                "processing_timestamp": datetime.now().isoformat(),
                "executive_summary": "Error occurred during analysis processing",
                "evidence_details": {
                    "full_transcript": transcript,
                    "audio_duration_seconds": audio_duration,
                    "processing_timestamp": datetime.now().isoformat(),
                    "threat_indicators": [],
                    "risk_assessment": risk_assessment
                },
                "error": str(e)
            }