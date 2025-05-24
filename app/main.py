# app/main.py
import os
import logging
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.config import settings
from app.models.request_models import AudioAssessmentRequest, SummarizerRequest
from app.models.response_models import AssessmentResponse, SummaryResponse, RiskLevel
from app.services.speech_service import AlibabaSpeechService
from app.services.qwen_service import QwenService
from app.services.risk_assessment import RiskAssessmentService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GoShield - Ride Safety Pipeline", version="1.0.0")

# Initialize services
speech_service = AlibabaSpeechService()
qwen_service = QwenService()
risk_service = RiskAssessmentService()

# Ensure temp directory exists
os.makedirs(settings.AUDIO_TEMP_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "GoShield API is running", "version": "1.0.0"}

@app.post("/api/assessment", response_model=AssessmentResponse)
async def assess_audio_risk(
    audio_file: UploadFile = File(...),
    driver_id: str = Form(None),
    location_lat: float = Form(None),
    location_lng: float = Form(None),
    route_expected: str = Form(None)
):
    """
    Main assessment API - takes 10-second audio slice and returns risk assessment
    """
    try:
        # Save uploaded audio temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav", 
                                       dir=settings.AUDIO_TEMP_DIR) as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_audio_path = temp_file.name
        
        try:
            # Step 1: Transcribe audio
            logger.info("Transcribing audio...")
            transcribed_text = speech_service.transcribe_audio(temp_audio_path)
            
            if not transcribed_text:
                logger.warning("No speech detected in audio")
                transcribed_text = "[No speech detected]"
            
            # Step 2: Assess threat level from text
            logger.info("Assessing threat level...")
            threat_text_score = qwen_service.assess_threat_level(transcribed_text)
            
            # Step 3: Calculate location risk
            location_risk = risk_service.calculate_location_risk(
                location_lat, location_lng, route_expected
            )
            
            # Step 4: Get driver history score
            driver_history_score = risk_service.get_driver_history_score(driver_id)
            
            # Step 5: Calculate overall risk
            overall_score, risk_level = risk_service.calculate_overall_risk(
                threat_text_score, location_risk, driver_history_score
            )
            
            # Step 6: Determine actions
            action_required = risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]
            push_notification = risk_service.get_push_notification_message(risk_level) if action_required else None
            
            logger.info(f"Risk assessment completed: {risk_level.value} ({overall_score:.2f})")
            
            return AssessmentResponse(
                risk_score=overall_score,
                risk_level=risk_level,
                threat_text_score=threat_text_score,
                location_risk_index=location_risk,
                driver_history_score=driver_history_score,
                transcribed_text=transcribed_text,
                action_required=action_required,
                push_notification=push_notification
            )
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
        
    except Exception as e:
        logger.error(f"Error in risk assessment: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")

@app.post("/api/summarize", response_model=SummaryResponse)
async def summarize_session(request: SummarizerRequest):
    """
    Summarizer API - creates incident summary (dummy implementation for hackathon)
    """
    try:
        # For hackathon: dummy implementation
        # Real implementation would:
        # 1. Fetch all audio slices for the session
        # 2. Combine transcriptions
        # 3. Use LLM to create comprehensive summary
        # 4. Count risk events and calculate statistics
        
        summary = f"""
        Incident Summary for Session {request.session_id}:
        
        - Total Duration: 15.5 minutes
        - Risk Events Detected: 2
        - Highest Risk Score: 67.5 (Medium Risk)
        - Key Concerns: Inappropriate comments detected at 8:30 and 12:15
        - Recommendation: Follow up with passenger for feedback
        
        This is a dummy summary for hackathon demonstration.
        In production, this would analyze the complete audio session.
        """
        
        return SummaryResponse(
            session_id=request.session_id,
            incident_summary=summary,
            total_risk_events=2,
            highest_risk_score=67.5,
            duration_minutes=15.5
        )
        
    except Exception as e:
        logger.error(f"Error in summarization: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")
    
# app/main.py (UPDATE assessment endpoint)
@app.post("/api/assessment", response_model=AssessmentResponse)
async def assess_audio_risk(
    audio_file: UploadFile = File(...),
    driver_id: str = Form(None),
    location_lat: float = Form(None),
    location_lng: float = Form(None),
    route_expected: str = Form(None)
):
    """
    Main assessment API - takes 10-second audio slice and returns risk assessment
    Supports: WAV, MP3, M4A, AAC, FLAC, OGG
    """
    try:
        # Validate file format
        if not AudioProcessor.is_supported_format(audio_file.filename):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported audio format. Supported: {AudioProcessor.SUPPORTED_FORMATS}"
            )
        
        # Determine file extension
        file_ext = os.path.splitext(audio_file.filename)[1] or '.wav'
        
        # Save uploaded audio temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext, 
                                       dir=settings.AUDIO_TEMP_DIR) as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_audio_path = temp_file.name
        
        try:
            logger.info(f"Processing {audio_file.filename} ({file_ext})")
            
            # Step 1: Transcribe audio (will auto-convert if needed)
            logger.info("Transcribing audio...")
            transcribed_text = speech_service.transcribe_audio(temp_audio_path)
            
            if not transcribed_text:
                logger.warning("No speech detected in audio")
                transcribed_text = "[No speech detected]"
            
            # Step 2: Assess threat level from text
            logger.info(f"Transcribed: '{transcribed_text}'")
            logger.info("Assessing threat level...")
            threat_text_score = qwen_service.assess_threat_level(transcribed_text)
            
            # Step 3: Calculate location risk
            location_risk = risk_service.calculate_location_risk(
                location_lat, location_lng, route_expected
            )
            
            # Step 4: Get driver history score
            driver_history_score = risk_service.get_driver_history_score(driver_id)
            
            # Step 5: Calculate overall risk
            overall_score, risk_level = risk_service.calculate_overall_risk(
                threat_text_score, location_risk, driver_history_score
            )
            
            # Step 6: Determine actions
            action_required = risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]
            push_notification = risk_service.get_push_notification_message(risk_level) if action_required else None
            
            logger.info(f"Assessment completed - Risk: {risk_level.value} ({overall_score:.2f})")
            logger.info(f"Breakdown - Threat: {threat_text_score}, Location: {location_risk}, Driver: {driver_history_score}")
            
            return AssessmentResponse(
                risk_score=round(overall_score, 2),
                risk_level=risk_level,
                threat_text_score=round(threat_text_score, 2),
                location_risk_index=round(location_risk, 2),
                driver_history_score=round(driver_history_score, 2),
                transcribed_text=transcribed_text,
                action_required=action_required,
                push_notification=push_notification
            )
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
        
    except Exception as e:
        logger.error(f"Error in risk assessment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")
    


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "services": "operational"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)