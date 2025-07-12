import os
import time
from typing import Optional, List, Dict, Any
from openai import OpenAI
from django.conf import settings


class LLMConnector:
    """Generic LLM connector that can be used by multiple services"""
    
    def __init__(self):
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize the OpenAI client with API key from database or environment"""
        try:
            # Try to get API key from database settings first
            from patients.models import Settings
            db_settings = Settings.get_settings()
            api_key = db_settings.openai_api_key
        except Exception:
            # Database might not be ready yet, use None
            api_key = None
        
        # Fall back to Django settings (which reads from .env)
        if not api_key:
            api_key = settings.OPENAI_API_KEY
        
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
    
    def is_available(self) -> bool:
        """Check if the LLM service is available"""
        return self.client is not None
    
    def reinitialize(self):
        """Reinitialize the client (useful after settings change)"""
        self._init_client()
    
    def transcribe(self, file_path: str, language: str = "de") -> tuple[str, float]:
        """
        Transcribe audio file using OpenAI Whisper
        Returns: (transcribed_text, processing_time_seconds)
        """
        if not self.is_available():
            raise ValueError("OpenAI API key nicht konfiguriert")
        
        start_time = time.time()
        
        try:
            with open(file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
                
            processing_time = time.time() - start_time
            return response.text, processing_time
            
        except Exception as e:
            raise Exception(f"Fehler bei der Transkription: {str(e)}")

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.3,
        model: str = "gpt-4.1-nano",
    ) -> str:
        """
        Generate text using OpenAI GPT models
        
        Args:
            system_prompt: The system prompt to set context
            user_prompt: The user prompt with the actual request
            max_tokens: Maximum tokens to generate
            temperature: Creativity level (0.0 = deterministic, 1.0 = very creative)
            model: The model to use
            
        Returns:
            Generated text
        """
        if not self.is_available():
            raise ValueError("OpenAI API key nicht konfiguriert")
        
        if not user_prompt.strip():
            return ""
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            
            response = self.client.chat.completions.create(
                model=model, 
                messages=messages, 
                max_tokens=max_tokens, 
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Fehler bei der Textgenerierung: {str(e)}")


# Singleton instance - lazy initialization
_llm_connector_instance = None

def get_llm_connector():
    """Get the singleton LLM connector instance"""
    global _llm_connector_instance
    if _llm_connector_instance is None:
        _llm_connector_instance = LLMConnector()
    return _llm_connector_instance 