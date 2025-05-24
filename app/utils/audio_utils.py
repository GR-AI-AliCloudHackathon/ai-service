# app/utils/audio_utils.py (UPDATE)
import os
import logging
import tempfile
from pydub import AudioSegment
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Handle various audio formats and convert to WAV for Alibaba ISI"""
    
    SUPPORTED_FORMATS = ['.wav', '.mp3', '.m4a', '.aac', '.flac', '.ogg']
    
    # Alibaba ISI Requirements
    TARGET_SAMPLE_RATE = 16000
    TARGET_SAMPLE_WIDTH = 2  # 16-bit
    TARGET_CHANNELS = 1      # Mono
    
    @staticmethod
    def needs_conversion(input_path: str) -> Tuple[bool, str]:
        """
        Check if audio needs conversion to meet Alibaba ISI requirements
        Returns: (needs_conversion, reason)
        """
        try:
            audio = AudioSegment.from_file(input_path)
            
            reasons = []
            if audio.frame_rate != AudioProcessor.TARGET_SAMPLE_RATE:
                reasons.append(f"sample_rate:{audio.frame_rate}→{AudioProcessor.TARGET_SAMPLE_RATE}")
            
            if audio.sample_width != AudioProcessor.TARGET_SAMPLE_WIDTH:
                reasons.append(f"bit_depth:{audio.sample_width*8}→{AudioProcessor.TARGET_SAMPLE_WIDTH*8}")
            
            if audio.channels != AudioProcessor.TARGET_CHANNELS:
                reasons.append(f"channels:{audio.channels}→{AudioProcessor.TARGET_CHANNELS}")
            
            needs_conv = len(reasons) > 0
            reason = ", ".join(reasons) if reasons else "already_compatible"
            
            return needs_conv, reason
            
        except Exception as e:
            logger.error(f"Error checking audio compatibility: {e}")
            return True, "error_checking"
    
    @staticmethod
    def convert_to_wav(input_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert audio file to WAV format suitable for Alibaba ISI
        ALWAYS ensures: 16kHz, 16-bit, Mono
        Returns path to the converted WAV file
        """
        try:
            logger.info(f"Loading audio file: {input_path}")
            
            # Load audio file (pydub automatically detects format)
            audio = AudioSegment.from_file(input_path)
            
            # Log original specs
            logger.info(f"Original audio specs: {audio.frame_rate}Hz, {audio.sample_width*8}-bit, {audio.channels}ch")
            
            # Convert to Alibaba ISI requirements
            original_specs = f"{audio.frame_rate}Hz/{audio.sample_width*8}bit/{audio.channels}ch"
            
            if audio.frame_rate != AudioProcessor.TARGET_SAMPLE_RATE:
                logger.info(f"Converting sample rate: {audio.frame_rate}Hz → {AudioProcessor.TARGET_SAMPLE_RATE}Hz")
                audio = audio.set_frame_rate(AudioProcessor.TARGET_SAMPLE_RATE)
            
            if audio.sample_width != AudioProcessor.TARGET_SAMPLE_WIDTH:
                logger.info(f"Converting bit depth: {audio.sample_width*8}-bit → {AudioProcessor.TARGET_SAMPLE_WIDTH*8}-bit")
                audio = audio.set_sample_width(AudioProcessor.TARGET_SAMPLE_WIDTH)
            
            if audio.channels != AudioProcessor.TARGET_CHANNELS:
                logger.info(f"Converting channels: {audio.channels} → {AudioProcessor.TARGET_CHANNELS} (mono)")
                audio = audio.set_channels(AudioProcessor.TARGET_CHANNELS)
            
            if output_path is None:
                # Create temporary WAV file
                temp_fd, output_path = tempfile.mkstemp(suffix='.wav')
                os.close(temp_fd)
            
            # Export as WAV with PCM encoding
            audio.export(output_path, format="wav", parameters=["-acodec", "pcm_s16le"])
            
            # Log conversion results
            final_specs = f"{AudioProcessor.TARGET_SAMPLE_RATE}Hz/{AudioProcessor.TARGET_SAMPLE_WIDTH*8}bit/{AudioProcessor.TARGET_CHANNELS}ch"
            logger.info(f"Audio conversion completed: {original_specs} → {final_specs}")
            logger.info(f"Duration: {len(audio)/1000:.2f} seconds")
            logger.info(f"Output file: {output_path}")
            
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
                'bit_depth': audio.sample_width * 8,
                'format': file_path.split('.')[-1].lower(),
                'file_size_bytes': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                'alibaba_isi_compatible': (
                    audio.frame_rate == AudioProcessor.TARGET_SAMPLE_RATE and
                    audio.sample_width == AudioProcessor.TARGET_SAMPLE_WIDTH and
                    audio.channels == AudioProcessor.TARGET_CHANNELS
                )
            }
        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            return {}
    
    @staticmethod
    def is_supported_format(filename: str) -> bool:
        """Check if audio format is supported"""
        ext = os.path.splitext(filename.lower())[1]
        return ext in AudioProcessor.SUPPORTED_FORMATS