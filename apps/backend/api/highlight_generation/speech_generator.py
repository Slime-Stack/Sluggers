import logging
from google.cloud import texttospeech

from apps.backend.config import BUCKET_URI
from apps.backend.utils.gcs_utils import upload_blob_from_stream

logger = logging.getLogger(__name__)

def synthesize_highlight_from_ssml(caption: str, language_code: str, act_number: int, scene_number: int) -> str:
    """
    Synthesizes speech from the input string of ssml and outputs the url of the storage location.

    Note: ssml must be well-formed according to:
       https://www.w3.org/TR/speech-synthesis/
    """
    logger.debug(f"Synthesizing speech for language {language_code}, scene {scene_number}")
    
    # Configuration mapping with proper enum values
    voice_configs = {
        "en": (
            texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Neural2-D"
            ),
            texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.15,
                pitch=-1.5
            )
        ),
        "es": (
            texttospeech.VoiceSelectionParams(
                language_code="es-US",
                name="es-US-Neural2-B"
            ),
            texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.15,
                pitch=-1.5
            )
        ),
        "ja": (
            texttospeech.VoiceSelectionParams(
                language_code="ja-JP",
                name="ja-JP-Neural2-C"
            ),
            texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.15,
                pitch=-1.5
            )
        )
    }

    if language_code not in voice_configs:
        error_msg = f"Unsupported language code: {language_code}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        # Prepare SSML input
        ssml = f"<speak>{caption}</speak>"
        input_text = texttospeech.SynthesisInput(ssml=ssml)
        
        # Get voice and audio config for the language
        voice, audio_config = voice_configs[language_code]
        
        # Generate speech
        logger.debug(f"Generating speech with {language_code} voice")
        tts_client = texttospeech.TextToSpeechClient()
        response = tts_client.synthesize_speech(
            input=input_text,
            voice=voice,
            audio_config=audio_config
        )
        
        # Upload to storage
        logger.debug(f"Uploading audio file for scene {scene_number}")
        bucket_name = BUCKET_URI.replace('gs://', '')
        blob_url = upload_blob_from_stream(
            bucket_name=bucket_name,
            destination_blob_name=_build_output_file_name(act_number, scene_number, language_code),
            content=response.audio_content
        )
        
        logger.info(f"Successfully generated and uploaded audio for {language_code}, scene {scene_number}")
        return blob_url

    except Exception as e:
        logger.error(f"Failed to synthesize speech for {language_code}, scene {scene_number}: {str(e)}", exc_info=True)
        raise

def _build_output_file_name(act_number: int, scene_number: int, language_code: str) -> str:
    """Build the output file name for the audio file."""
    return f"sluggers_tts_{act_number}{scene_number}{language_code}.mp3"
