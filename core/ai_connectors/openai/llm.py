"""OpenAI LLM connector"""

from openai import OpenAI
from django.conf import settings

from ..base.llm import GenericLLMConnector, LLMGenerationParams, LLMResult
from ..base.exceptions import LLMError, ConfigurationError


class OpenAILLMConnector(GenericLLMConnector):
    """OpenAI GPT implementation for text generation"""
    
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
        """Check if the LLM service is available"""
        return self.client is not None
    
    def generate_text(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        params: LLMGenerationParams
    ) -> LLMResult:
        """
        Generate text using OpenAI GPT models
        
        Args:
            system_prompt: System prompt to set context
            user_prompt: User prompt with the actual request
            params: Generation parameters
            
        Returns:
            LLMResult with generated text and metadata
        """
        if not self.is_available():
            raise ConfigurationError("OpenAI API key nicht konfiguriert")
        
        if not user_prompt.strip():
            return LLMResult(text="")
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            
            response = self.client.chat.completions.create(
                model=params.model or "gpt-4.1-nano",
                messages=messages,
                max_tokens=params.max_tokens,
                temperature=params.temperature
            )
            
            return LLMResult(
                text=response.choices[0].message.content.strip(),
                usage_tokens=response.usage.total_tokens if response.usage else None,
                model_used=response.model
            )
            
        except Exception as e:
            raise LLMError(f"Fehler bei der Textgenerierung: {str(e)}")
    
    def get_available_models(self) -> list[str]:
        """Get list of available OpenAI models"""
        return ["gpt-4.1-nano", "gpt-4", "gpt-3.5-turbo"]
    
    def reinitialize(self) -> None:
        """Reinitialize the OpenAI client"""
        self._init_client() 