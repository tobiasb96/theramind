"""Custom exceptions for AI connectors"""


class AIConnectorError(Exception):
    """Base exception for AI connector errors"""
    pass


class ConfigurationError(AIConnectorError):
    """Raised when connector configuration is invalid or missing"""
    pass


class TranscriptionError(AIConnectorError):
    """Raised when transcription fails"""
    pass


class LLMError(AIConnectorError):
    """Raised when LLM text generation fails"""
    pass 