import io
from google.cloud import texttospeech
from apps.config import BUCKET_URI
from apps.backend.utils.gcs_utils import upload_blob_from_stream

class SpeechGenerator:
    """
    A class to generate audio using the Text-to-Speech API.
    """
    scene_id: str

    AUDIO_FILE_NAME_PREFIX = "sluggers_tts_"
    AUDIO_FILE_NAME_SUFFIX = ".mp3"

    def __init__(self):
        self.tts_client = texttospeech.TextToSpeechClient()
        self._build_output_file_name(self.scene_id)


    def synthesize_highlight_from_ssml(self, text: str) -> None:
        """
        Synthesizes speech from the input string of ssml.

        Note: ssml must be well-formed according to:
           https://www.w3.org/TR/speech-synthesis/

        Args:
           text (str): Text to be converted to audio.
        """
        ssml = f"<speak>{text}</speak>"
        input_text = texttospeech.SynthesisInput()
        input_text.ssml = ssml

        voice = texttospeech.VoiceSelectionParams()
        voice.language_code="en-US"
        voice.name="en-US-Neural2-D"
        voice.ssml_gender=texttospeech.SsmlVoiceGender.MALE,

        audio_config = texttospeech.AudioConfig()
        audio_config.audio_encoding = texttospeech.AudioEncoding.MP3
        audio_config.speaking_rate=1.15
        audio_config.pitch=0.5

        response = self.tts_client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
        # Create BytesIO object for cloud storage upload
        file_obj = io.BytesIO()
        file_obj.write(response.audio_content)
        # Remove 'gs://' from the bucket name
        bucket_name = BUCKET_URI.replace('gs://', '')
        upload_blob_from_stream(bucket_name, file_obj, self.OUTPUT_FILE_NAME)


    def _build_output_file_name(self, scene_id):
        self.OUTPUT_FILE_NAME = f"{self.AUDIO_FILE_NAME_PREFIX}{scene_id}{self.AUDIO_FILE_NAME_SUFFIX}"
