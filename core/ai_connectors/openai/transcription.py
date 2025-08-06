"""OpenAI Whisper transcription connector"""
import tempfile
import time
from openai import OpenAI
from django.conf import settings
from pydub import AudioSegment

from ..base.transcription import GenericTranscriptionConnector, TranscriptionResult
from ..base.exceptions import TranscriptionError, ConfigurationError


class OpenAIWhisperConnector(GenericTranscriptionConnector):
    """OpenAI Whisper implementation for transcription"""
    
    def __init__(self):
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize the OpenAI client with API key from settings"""
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
    
    def is_available(self) -> bool:
        """Check if the transcription service is available"""
        return self.client is not None
    
    def transcribe(self, file_path: str, language: str = "de") -> TranscriptionResult:
        """
        Transcribe audio file using OpenAI Whisper
        
        Args:
            file_path: Path to the audio file
            language: Language code for transcription
            
        Returns:
            TranscriptionResult with transcribed text and metadata
        """
        if not self.is_available():
            raise ConfigurationError("OpenAI API key nicht konfiguriert")
        
        start_time = time.time()
        
        try:
            audio = AudioSegment.from_file(file_path)
            results = []
            chunk_length_ms = 600_000  # 10 minute chunks
            for i in range(0, len(audio), chunk_length_ms):
                chunk = audio[i:i + chunk_length_ms]
                with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_audio:
                    chunk.export(temp_audio.name, format="mp3")
                    result = self._transcribe(temp_audio.name, language=language)
                    results.append(result)
            
            processing_time = time.time() - start_time
            
            return TranscriptionResult(
                text=" ".join(results),
                processing_time=processing_time,
                language=language
            )
            
        except Exception as e:
            raise TranscriptionError(f"Fehler bei der Transkription: {str(e)}")

    def _transcribe(self, file_path: str, language: str = "de") -> str:
        with open(file_path, "rb") as audio_file:
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language
            )
        return response.text
    
    def get_supported_formats(self) -> list[str]:
        """Get list of supported audio formats for OpenAI Whisper"""
        return ["mp3", "wav", "m4a", "webm", "flac"]
    
    def reinitialize(self) -> None:
        """Reinitialize the OpenAI client"""
        self._init_client() 