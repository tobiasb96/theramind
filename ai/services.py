import os
import time
from typing import Optional
from openai import OpenAI
from django.conf import settings


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
        Summarize text using OpenAI GPT
        """
        if not self.is_available():
            raise ValueError("OpenAI API key nicht konfiguriert")
        
        if not text.strip():
            return ""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Du bist ein Assistent für Psychotherapeuten. Fasse Therapiesitzungen professionell und strukturiert zusammen. Konzentriere dich auf wichtige Themen, Fortschritte und Erkenntnisse."
                },
                {
                    "role": "user",
                    "content": f"Fasse folgende Therapiesitzung in 150-200 Wörtern zusammen. Strukturiere die Zusammenfassung mit Hauptthemen, wichtigen Erkenntnissen und nächsten Schritten:\n\n{text}"
                }
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Fehler bei der Zusammenfassung: {str(e)}")
    
    def analyze_sentiment(self, text: str) -> dict:
        """
        Analyze sentiment and emotional tone of therapy session
        """
        if not self.is_available():
            raise ValueError("OpenAI API key nicht konfiguriert")
        
        if not text.strip():
            return {"sentiment": "neutral", "confidence": 0.0, "key_emotions": []}
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Du bist ein Experte für emotionale Analyse von Therapiesitzungen. Analysiere den emotionalen Ton und die Stimmung des Patienten."
                },
                {
                    "role": "user",
                    "content": f"Analysiere die emotionale Stimmung in folgendem Therapietext. Gib die Antwort als JSON zurück mit: sentiment (positiv/neutral/negativ), confidence (0-1), key_emotions (Liste der Hauptemotionen):\n\n{text[:2000]}"
                }
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=150,
                temperature=0.1
            )
            
            # Simple fallback parsing if JSON parsing fails
            content = response.choices[0].message.content.strip()
            try:
                import json
                return json.loads(content)
            except:
                return {"sentiment": "neutral", "confidence": 0.5, "key_emotions": ["unbekannt"]}
                
        except Exception as e:
            return {"sentiment": "neutral", "confidence": 0.0, "key_emotions": ["fehler"], "error": str(e)}


# Singleton instance - lazy initialization
_ai_service_instance = None

def get_ai_service():
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance

# For backward compatibility
ai_service = None  # Will be initialized when first accessed