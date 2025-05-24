# app/services/qwen_service.py
import json
import logging
from openai import OpenAI
from app.config import settings

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