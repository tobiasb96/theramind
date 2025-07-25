"""Factory for creating AI connectors with singleton management"""

from typing import Type
from django.conf import settings

from .base.transcription import GenericTranscriptionConnector
from .base.llm import GenericLLMConnector
from .openai.transcription import OpenAIWhisperConnector
from .openai.llm import OpenAILLMConnector


class ConnectorFactory:
    """Factory for creating AI connectors based on configuration"""
    
    _transcription_connectors = {
        'openai': OpenAIWhisperConnector,
        # Future providers can be added here:
        # 'azure': AzureWhisperConnector,
        # 'google': GoogleSpeechConnector,
    }
    
    _llm_connectors = {
        'openai': OpenAILLMConnector,
        # Future providers can be added here:
        # 'azure': AzureOpenAIConnector,
        # 'anthropic': AnthropicConnector,
    }
    
    @classmethod
    def get_transcription_connector(
        cls, 
        provider: str = None
    ) -> GenericTranscriptionConnector:
        """Get transcription connector instance"""
        provider = provider or getattr(settings, 'DEFAULT_TRANSCRIPTION_PROVIDER', 'openai')
        
        if provider not in cls._transcription_connectors:
            raise ValueError(f"Unknown transcription provider: {provider}")
        
        connector_class = cls._transcription_connectors[provider]
        return connector_class()
    
    @classmethod
    def get_llm_connector(cls, provider: str = None) -> GenericLLMConnector:
        """Get LLM connector instance"""
        provider = provider or getattr(settings, 'DEFAULT_LLM_PROVIDER', 'openai')
        
        if provider not in cls._llm_connectors:
            raise ValueError(f"Unknown LLM provider: {provider}")
        
        connector_class = cls._llm_connectors[provider]
        return connector_class()


# Singleton instances with lazy initialization
_transcription_connector = None
_llm_connector = None


def get_transcription_connector() -> GenericTranscriptionConnector:
    """Get singleton transcription connector"""
    global _transcription_connector
    if _transcription_connector is None:
        _transcription_connector = ConnectorFactory.get_transcription_connector()
    return _transcription_connector


def get_llm_connector() -> GenericLLMConnector:
    """Get singleton LLM connector"""
    global _llm_connector
    if _llm_connector is None:
        _llm_connector = ConnectorFactory.get_llm_connector()
    return _llm_connector


def reinitialize_connectors():
    """Reinitialize all singleton connectors (useful after settings changes)"""
    global _transcription_connector, _llm_connector
    
    if _transcription_connector:
        _transcription_connector.reinitialize()
    
    if _llm_connector:
        _llm_connector.reinitialize() 