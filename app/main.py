# app/main.py
import os
import logging
import tempfile
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.models.request_models import AudioAssessmentRequest, SummarizerRequest
from app.models.response_models import AssessmentResponse, SummaryResponse, RiskLevel
from app.services.speech_service import AlibabaSpeechService
from app.services.qwen_service import QwenService
from app.services.risk_assessment import RiskAssessmentService
from app.utils.audio_utils import AudioProcessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GoShield - Ride Safety Pipeline", version="1.0.0")

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Alternative frontend port
        "https://your-domain.com",  # Add your production domain when deployed
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

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

# app/main.py (UPDATE the summarize endpoint)
@app.post("/api/summarize")
async def create_evidence_kit(
    audio_file: UploadFile = File(...),
    incident_id: str = Form(None),
    ride_id: str = Form(None),
    passenger_id: str = Form(None),
    driver_id: str = Form(None),
    additional_context: str = Form(None)
):
    """
    Create Evidence Kit from Audio File
    - Transcribes audio using Alibaba ISI
    - Performs comprehensive threat analysis using Qwen
    - Creates structured evidence kit as JSON
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
            logger.info(f"Creating evidence kit for {audio_file.filename}")
            
            # Step 1: Get audio information
            audio_info = AudioProcessor.get_audio_info(temp_audio_path)
            audio_duration = audio_info.get('duration_seconds', 0)
            
            # Step 2: Transcribe audio
            logger.info("Transcribing audio for evidence kit...")
            transcribed_text = speech_service.transcribe_audio(temp_audio_path)
            
            if not transcribed_text:
                logger.warning("No speech detected in audio")
                transcribed_text = "[No clear speech detected in audio file]"
            
            logger.info(f"Transcription completed: {len(transcribed_text)} characters")
            
            # Step 3: Perform basic threat assessment for context
            threat_score = qwen_service.assess_threat_level(transcribed_text)
            
            # Step 4: Create risk assessment context
            risk_assessment = {
                "threat_text_score": threat_score,
                "overall_score": threat_score,  # Simplified for evidence kit
                "assessment_type": "full_audio_analysis",
                "processing_method": "comprehensive_review"
            }
            
            # Step 5: Prepare ride context
            ride_context = {
                "incident_id": incident_id,
                "ride_id": ride_id,
                "passenger_id": passenger_id,
                "driver_id": driver_id,
                "additional_context": additional_context,
                "audio_filename": audio_file.filename,
                "file_size_bytes": len(content)
            }
            
            # Step 6: Create comprehensive evidence kit
            logger.info("Generating comprehensive evidence kit...")
            evidence_kit = qwen_service.create_evidence_kit(
                transcript=transcribed_text,
                audio_duration=audio_duration,
                risk_assessment=risk_assessment,
                ride_context=ride_context
            )
            
            logger.info(f"Evidence kit created successfully: {evidence_kit['evidence_kit_id']}")
            
            return evidence_kit
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
        
    except Exception as e:
        logger.error(f"Error creating evidence kit: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Evidence kit creation failed: {str(e)}")

# Also add a simplified endpoint for just transcript extraction
@app.post("/api/transcribe")
async def transcribe_audio_only(audio_file: UploadFile = File(...)):
    """
    Simple endpoint to just get transcript from audio
    """
    try:
        if not AudioProcessor.is_supported_format(audio_file.filename):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported audio format. Supported: {AudioProcessor.SUPPORTED_FORMATS}"
            )
        
        file_ext = os.path.splitext(audio_file.filename)[1] or '.wav'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext, 
                                       dir=settings.AUDIO_TEMP_DIR) as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_audio_path = temp_file.name
        
        try:
            audio_info = AudioProcessor.get_audio_info(temp_audio_path)
            transcribed_text = speech_service.transcribe_audio(temp_audio_path)
            
            return {
                "transcript": transcribed_text or "[No speech detected]",
                "audio_info": audio_info,
                "filename": audio_file.filename,
                "processing_timestamp": datetime.now().isoformat()
            }
            
        finally:
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
        
    except Exception as e:
        logger.error(f"Error in transcription: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")      

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "services": "operational"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)