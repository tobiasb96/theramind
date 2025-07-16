from core.connector import get_llm_connector
from transcriptions.prompts import (
    SUMMARY_PROMPT,
    SYSTEM_PROMPT_SUMMARY,
    SYSTEM_PROMPT,  # Fallback
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

    def _build_session_context_prefix(self, transcript_text: str) -> str:
        """
        Build the context prefix for session notes generation

        Args:
            transcript_text: The transcript text

        Returns:
            Formatted context prefix
        """
        context_prefix = f"""Erstelle strukturierte Sitzungsnotizen basierend auf dem folgenden Transkript einer Therapiesitzung.

Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

**TRANSKRIPT DER SITZUNG**
{transcript_text}

**SITZUNGSNOTIZEN**

"""
        return context_prefix

    def create_session_notes_with_template(self, transcript_text: str, template) -> str:
        """
        Create structured session notes using a specific template

        Args:
            transcript_text: The transcript text
            template: DocumentTemplate instance

        Returns:
            Generated session notes
        """
        if not transcript_text.strip():
            return ""

        try:
            # Build context prefix with transcript
            context_prefix = self._build_session_context_prefix(transcript_text)

            # Combine context prefix with template structure
            full_prompt = context_prefix + template.user_prompt

            # Use hardcoded system prompt
            return self.connector.generate_text(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=full_prompt,
                max_tokens=template.max_tokens,
                temperature=template.temperature,
            )

        except Exception as e:
            raise Exception(f"Fehler bei der Erstellung der Sitzungsnotizen: {str(e)}")

    def create_session_notes(self, transcript_text: str, template_key: str) -> str:
        """
        Create structured session notes using a template key (legacy method)

        Args:
            transcript_text: The transcript text
            template_key: Template key for backwards compatibility

        Returns:
            Generated session notes
        """
        # Import here to avoid circular imports
        from documents.models import DocumentTemplate
        from documents.services import TemplateService

        template_service = TemplateService()
        templates = template_service.get_session_templates()

        # Find template by matching name with template_key
        template = None
        template_key_mapping = {
            "erstgespraech": "Erstgespräch",
            "verlaufsgespraech": "Verlaufsgespräch",
            "abschlussgespraech": "Abschlussgespräch",
        }

        target_name = template_key_mapping.get(template_key, template_key)

        for t in templates:
            if t.name == target_name:
                template = t
                break

        if not template:
            # Fall back to first available template
            template = templates[0] if templates else None

        if not template:
            raise ValueError(f"Kein Template gefunden für: {template_key}")

        return self.create_session_notes_with_template(transcript_text, template)


# Singleton instance - lazy initialization
_transcription_service_instance = None

def get_transcription_service():
    global _transcription_service_instance
    if _transcription_service_instance is None:
        _transcription_service_instance = TranscriptionService()
    return _transcription_service_instance
