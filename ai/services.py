import os
import time
from typing import Optional
from openai import OpenAI
from django.conf import settings
from .prompts import SUMMARY_PROMPT, get_session_notes_prompt


class AIService:
    def __init__(self):
        self.client = None
        self._init_client()
    
    def _init_client(self):
        try:
            # Try to get API key from database settings first
            from core.models import Settings
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
        return self.client is not None
    
    def reinitialize(self):
        """Reinitialize the client (useful after settings change)"""
        self._init_client()
    
    def transcribe(self, file_path: str) -> tuple[str, float]:
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
                    language="de"
                )
                
            processing_time = time.time() - start_time
            return response.text, processing_time
            
        except Exception as e:
            raise Exception(f"Fehler bei der Transkription: {str(e)}")
    
    def summarize(self, text: str) -> str:
        """
        Create ultra-short summary using OpenAI GPT
        """
        if not self.is_available():
            raise ValueError("OpenAI API key nicht konfiguriert")
        
        if not text.strip():
            return ""
        
        try:
            # Use the prompt from prompts.py
            prompt = SUMMARY_PROMPT.format(transcript=text)

            messages = [
                {
                    "role": "system",
                    "content": "Du bist ein Assistent für Psychotherapeuten. Erstelle präzise, kurze Zusammenfassungen von Therapiesitzungen.",
                },
                {"role": "user", "content": prompt},
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", messages=messages, max_tokens=150, temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Fehler bei der Zusammenfassung: {str(e)}")

    def create_session_notes(self, transcript_text: str, template_key: str) -> str:
        """
        Create structured session notes using a specific template
        """
        if not self.is_available():
            raise ValueError("OpenAI API key nicht konfiguriert")

        if not transcript_text.strip():
            return ""
        
        try:
            # Get the appropriate prompt template
            prompt = get_session_notes_prompt(template_key)
            formatted_prompt = prompt.format(transcript=transcript_text)

            messages = [
                {
                    "role": "system",
                    "content": "Du bist ein erfahrener Psychotherapeut. Erstelle strukturierte, professionelle Sitzungsnotizen basierend auf den bereitgestellten Transkripten.",
                },
                {"role": "user", "content": formatted_prompt},
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", messages=messages, max_tokens=1000, temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise Exception(f"Fehler bei der Erstellung der Sitzungsnotizen: {str(e)}")


# Singleton instance - lazy initialization
_ai_service_instance = None

def get_ai_service():
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance

# For backward compatibility
ai_service = None  # Will be initialized when first accessed