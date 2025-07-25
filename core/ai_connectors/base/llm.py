"""Generic LLM connector interface"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class LLMGenerationParams:
    """Parameters for LLM text generation"""
    max_tokens: int = 1000
    temperature: float = 0.3
    model: Optional[str] = None


@dataclass
class LLMResult:
    """Result of LLM text generation"""
    text: str
    usage_tokens: Optional[int] = None
    model_used: Optional[str] = None


class GenericLLMConnector(ABC):
    """Abstract base class for LLM text generation services"""
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM service is available"""
        pass
    
    @abstractmethod
    def generate_text(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        params: LLMGenerationParams
    ) -> LLMResult:
        """
        Generate text using the LLM
        
        Args:
            system_prompt: System prompt to set context
            user_prompt: User prompt with the actual request
            params: Generation parameters
            
        Returns:
            LLMResult with generated text and metadata
            
        Raises:
            LLMError: If text generation fails
            ConfigurationError: If service is not properly configured
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Get list of available models"""
        pass
    
    @abstractmethod
    def reinitialize(self) -> None:
        """Reinitialize the connector (useful after configuration changes)"""
        pass 