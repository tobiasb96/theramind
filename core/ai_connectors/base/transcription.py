"""Generic transcription connector interface"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class TranscriptionResult:
    """Result of audio transcription"""
    text: str
    processing_time: float
    confidence: Optional[float] = None
    language: Optional[str] = None


class GenericTranscriptionConnector(ABC):
    """Abstract base class for audio transcription services"""
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the transcription service is available"""
        pass
    
    @abstractmethod
    def transcribe(self, file_path: str, language: str = "de") -> TranscriptionResult:
        """
        Transcribe audio file
        
        Args:
            file_path: Path to the audio file
            language: Language code for transcription
            
        Returns:
            TranscriptionResult with transcribed text and metadata
            
        Raises:
            TranscriptionError: If transcription fails
            ConfigurationError: If service is not properly configured
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> list[str]:
        """Get list of supported audio formats"""
        pass
    
    @abstractmethod
    def reinitialize(self) -> None:
        """Reinitialize the connector (useful after configuration changes)"""
        pass 