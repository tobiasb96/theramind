from core.connector import get_llm_connector
from transcriptions.prompts import (
    SUMMARY_PROMPT,
    SYSTEM_PROMPT_SUMMARY,
    get_session_notes_prompt,
    SYSTEM_PROMPT,
)


class TranscriptionService:
    def __init__(self):
        self.connector = get_llm_connector()

    def is_available(self) -> bool:
        return self.connector.is_available()

    def reinitialize(self):
        """Reinitialize the client (useful after settings change)"""
        self.connector.reinitialize()

    def transcribe(self, file_path: str) -> tuple[str, float]:
        """
        Transcribe audio file using OpenAI Whisper
        Returns: (transcribed_text, processing_time_seconds)
        """
        return self.connector.transcribe(file_path)

    def summarize_session_notes(self, session_notes: str) -> str:
        """
        Create ultra-short summary using OpenAI GPT
        """
        prompt = SUMMARY_PROMPT.format(session_notes=session_notes)
        return self.connector.generate_text(SYSTEM_PROMPT_SUMMARY, prompt, max_tokens=100)

    def create_session_notes(self, transcript_text: str, template_key: str) -> str:
        """
        Create structured session notes using a specific template
        """
        if not transcript_text.strip():
            return ""

        try:
            # Get the appropriate prompt template
            prompt = get_session_notes_prompt(template_key)
            formatted_prompt = prompt.format(transcript=transcript_text)

            return self.connector.generate_text(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=formatted_prompt,
                max_tokens=1000,
                temperature=0.3,
            )

        except Exception as e:
            raise Exception(f"Fehler bei der Erstellung der Sitzungsnotizen: {str(e)}")


# Singleton instance - lazy initialization
_transcription_service_instance = None

def get_transcription_service():
    global _transcription_service_instance
    if _transcription_service_instance is None:
        _transcription_service_instance = TranscriptionService()
    return _transcription_service_instance
