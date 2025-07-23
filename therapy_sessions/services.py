from core.connector import get_llm_connector
from therapy_sessions.prompts import (
    SUMMARY_PROMPT,
    SYSTEM_PROMPT_SUMMARY,
    SYSTEM_PROMPT,  # Fallback
)


class TranscriptionService:
    """
    Service focused on AI-powered text generation tasks for therapy sessions.
    File transcription is now handled by the UnifiedInputService.
    """
    def __init__(self):
        self.connector = get_llm_connector()

    def is_available(self) -> bool:
        return self.connector.is_available()

    def reinitialize(self):
        """Reinitialize the client (useful after settings change)"""
        self.connector.reinitialize()

    # NOTE: transcribe method removed - now handled by UnifiedInputService

    def summarize_session_notes(self, session_notes: str) -> str:
        """
        Create ultra-short summary using OpenAI GPT
        """
        prompt = SUMMARY_PROMPT.format(session_notes=session_notes)
        return self.connector.generate_text(SYSTEM_PROMPT_SUMMARY, prompt, max_tokens=100)

    def _build_session_context_prefix(
        self, transcript_text: str, existing_notes: str = None, patient_gender: str = None
    ) -> str:
        """
        Build the context prefix for session notes generation

        Args:
            transcript_text: The transcript text
            existing_notes: Existing session notes (if any)
            patient_gender: The patient's gender for appropriate language use

        Returns:
            Formatted context prefix
        """
        context_prefix = f"""Erstelle strukturierte Sitzungsnotizen basierend auf dem folgenden Transkript einer Therapiesitzung.

Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

"""

        # Add patient gender context if provided
        if patient_gender and patient_gender != "not_specified":
            gender_mapping = {"male": "männlich", "female": "weiblich", "diverse": "divers"}
            gender_display = gender_mapping.get(patient_gender, "nicht angegeben")

            pronouns_mapping = {
                "male": "er/ihm/sein",
                "female": "sie/ihr/ihre",
                "diverse": "sie/dey/deren (verwende geschlechtsneutrale Sprache)",
            }
            pronouns = pronouns_mapping.get(patient_gender, "")

            context_prefix += f"""**PATIENT*INNEN-INFORMATIONEN**
Das Geschlecht des Patienten ist {gender_display}. Verwende entsprechende Pronomen ({pronouns}) und
geschlechtsangemessene Sprache in den Notizen. Achte auf eine respektvolle und professionelle Darstellung.

"""

        context_prefix += f"""**TRANSKRIPT DER SITZUNG**
{transcript_text}

"""

        # Include existing notes if they exist
        if existing_notes and existing_notes.strip():
            context_prefix += f"""**VORHANDENE NOTIZEN**
                Die folgenden Notizen existieren bereits für diese Sitzung. Bitte berücksichtige diese und
                erweitere sie sinnvoll mit den Informationen aus dem Transkript, wo es angemessen ist.
                Füge keine neuen Abschnitte hinzu:
                1. Entweder erweitere die bestehenden Abschnitte wenn das neue Format mit dem vorhandenen Format kompatibel ist.
                2. Oder ersetze die bestehenden Abschnitte mit dem neuen Format, schau dir aber den Inhalt an und übertrage
                wenn es sinnvoll ist.

                {existing_notes}

                """

        context_prefix += "**SITZUNGSNOTIZEN**\n\n"

        return context_prefix

    def create_session_notes_with_template(
        self, transcript_text: str, template, existing_notes: str = None, patient_gender: str = None
    ) -> str:
        """
        Create structured session notes using a specific template

        Args:
            transcript_text: The transcript text
            template: DocumentTemplate instance
            existing_notes: Existing session notes (if any)
            patient_gender: The patient's gender for appropriate language use

        Returns:
            Generated session notes
        """
        if not transcript_text.strip():
            return ""

        try:
            # Build context prefix with transcript and existing notes
            context_prefix = self._build_session_context_prefix(
                transcript_text, existing_notes, patient_gender
            )

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

    def create_session_notes(
        self,
        transcript_text: str,
        template_key: str,
        existing_notes: str = None,
        patient_gender: str = None,
    ) -> str:
        """
        Create structured session notes using a template key (legacy method)

        Args:
            transcript_text: The transcript text
            template_key: Template key for backwards compatibility
            existing_notes: Existing session notes (if any)
            patient_gender: The patient's gender for appropriate language use

        Returns:
            Generated session notes
        """
        # Import here to avoid circular imports
        from document_templates.service import TemplateService

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

        return self.create_session_notes_with_template(
            transcript_text, template, existing_notes, patient_gender
        )


# Singleton instance - lazy initialization
_transcription_service_instance = None

def get_transcription_service():
    global _transcription_service_instance
    if _transcription_service_instance is None:
        _transcription_service_instance = TranscriptionService()
    return _transcription_service_instance
