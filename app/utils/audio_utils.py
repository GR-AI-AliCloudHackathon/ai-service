# app/utils/audio_utils.py
import os
import logging
import tempfile
from pydub import AudioSegment
from typing import Optional

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Handle various audio formats and convert to WAV for Alibaba ISI"""
    
    SUPPORTED_FORMATS = ['.wav', '.mp3', '.m4a', '.aac', '.flac', '.ogg']
    
    @staticmethod
    def convert_to_wav(input_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert audio file to WAV format suitable for Alibaba ISI
        Returns path to the converted WAV file
        """
        try:
            # Load audio file (pydub automatically detects format)
            audio = AudioSegment.from_file(input_path)
            
            # Convert to the format Alibaba ISI expects:
            # - 16 kHz sample rate
            # - 16-bit depth  
            # - Mono channel
            audio = audio.set_frame_rate(16000)
            audio = audio.set_sample_width(2)  # 16-bit
            audio = audio.set_channels(1)      # Mono
            
            if output_path is None:
                # Create temporary WAV file
                temp_fd, output_path = tempfile.mkstemp(suffix='.wav')
                os.close(temp_fd)
            
            # Export as WAV
            audio.export(output_path, format="wav")
            
            logger.info(f"Audio converted: {input_path} -> {output_path}")
            logger.info(f"Duration: {len(audio)/1000:.2f} seconds")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting audio {input_path}: {e}")
            raise ValueError(f"Failed to convert audio: {str(e)}")
    
    @staticmethod
    def get_audio_info(file_path: str) -> dict:
        """Get audio file information"""
        try:
            audio = AudioSegment.from_file(file_path)
            return {
                'duration_seconds': len(audio) / 1000,
                'sample_rate': audio.frame_rate,
                'channels': audio.channels,
                'sample_width': audio.sample_width,
                'format': file_path.split('.')[-1].lower()
            }
        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            return {}
    
    @staticmethod
    def is_supported_format(filename: str) -> bool:
        """Check if audio format is supported"""
        ext = os.path.splitext(filename.lower())[1]
        return ext in AudioProcessor.SUPPORTED_FORMATS