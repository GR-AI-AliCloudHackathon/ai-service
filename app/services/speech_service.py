# app/services/speech_service.py (UPDATE)
import http.client
import json
import logging
import os
from app.config import settings
from app.utils.audio_utils import AudioProcessor

logger = logging.getLogger(__name__)

class AlibabaSpeechService:
    def __init__(self):
        self.host = f'nls-gateway-{settings.ALIBABA_REGION}.aliyuncs.com'
        self.token = self._get_token()
        self.audio_processor = AudioProcessor()
    
    def _get_token(self):
        """Get access token from Alibaba Cloud"""
        from aliyunsdkcore.client import AcsClient
        from aliyunsdkcore.request import CommonRequest
        
        client = AcsClient(
            settings.ALIBABA_ACCESS_KEY_ID,
            settings.ALIBABA_ACCESS_KEY_SECRET,
            settings.ALIBABA_REGION
        )
        
        request = CommonRequest()
        request.set_method('POST')
        request.set_domain(f'nlsmeta.{settings.ALIBABA_REGION}.aliyuncs.com')
        request.set_version('2019-07-17')
        request.set_action_name('CreateToken')
        
        try:
            response = client.do_action_with_exception(request)
            response_json = json.loads(response)
            return response_json.get("Token", {}).get("Id")
        except Exception as e:
            logger.error(f"Failed to get Alibaba token: {e}")
            raise
    
    # app/services/speech_service.py (UPDATE transcribe_audio method)
    def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio using Alibaba ISI Short Sentence Recognition"""
        wav_path = None
        try:
            # Get audio info for logging
            audio_info = self.audio_processor.get_audio_info(audio_file_path)
            logger.info(f"Input audio specs: {audio_info}")
            
            # Check if conversion is needed (regardless of format)
            needs_conv, reason = self.audio_processor.needs_conversion(audio_file_path)
            
            if needs_conv:
                logger.info(f"Audio conversion needed: {reason}")
                wav_path = self.audio_processor.convert_to_wav(audio_file_path)
                processing_path = wav_path
            else:
                logger.info("Audio already compatible with Alibaba ISI requirements")
                processing_path = audio_file_path
            
            # Verify final audio specs
            final_info = self.audio_processor.get_audio_info(processing_path)
            logger.info(f"Processing audio specs: {final_info}")
            
            if not final_info.get('alibaba_isi_compatible', False):
                logger.warning("Audio may not be fully compatible with Alibaba ISI!")
            
            # Read the processed audio file
            with open(processing_path, mode='rb') as f:
                audio_content = f.read()
            
            logger.info(f"Audio file size: {len(audio_content)} bytes")
            
            # Configure request for short sentence recognition
            url = (f'/stream/v1/asr?appkey={settings.ALIBABA_APPKEY}'
                f'&format=pcm&sample_rate=16000'
                f'&enable_punctuation_prediction=true'
                f'&enable_inverse_text_normalization=true'
                f'&enable_voice_detection=false')
            
            headers = {
                'X-NLS-Token': self.token,
                'Content-type': 'application/octet-stream',
                'Content-Length': str(len(audio_content))
            }
            
            logger.info(f"Making request to: {self.host}{url}")
            
            # Make request
            conn = http.client.HTTPConnection(self.host)
            conn.request(method='POST', url=url, body=audio_content, headers=headers)
            
            response = conn.getresponse()
            body = response.read()
            
            logger.info(f"Response status: {response.status} {response.reason}")
            
            if response.status == 200:
                result = json.loads(body)
                logger.info(f"API Response: {result}")
                
                if result.get('status') == 20000000:
                    transcribed_text = result.get('result', '')
                    logger.info(f"✅ Transcription successful: '{transcribed_text}'")
                    return transcribed_text
                else:
                    logger.error(f"❌ Speech recognition failed - Status: {result.get('status')}, Message: {result.get('message', 'Unknown error')}")
                    return ""
            else:
                logger.error(f"❌ HTTP error: {response.status} {response.reason}")
                logger.error(f"Response body: {body.decode('utf-8', errors='ignore')}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Error in speech transcription: {e}", exc_info=True)
            return ""
        finally:
            # Clean up temporary WAV file
            if wav_path and os.path.exists(wav_path):
                try:
                    os.unlink(wav_path)
                    logger.info("Temporary WAV file cleaned up")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup temp file: {cleanup_error}")
            if 'conn' in locals():
                conn.close()