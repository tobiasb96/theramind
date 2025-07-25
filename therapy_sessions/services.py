from typing import Optional
from django.db.models import Q
from core.ai_connectors import get_llm_connector
from core.ai_connectors.base.llm import LLMGenerationParams
from core.utils.ai_helpers import build_gender_context
from core.services import UnifiedInputService
from document_templates.models import DocumentTemplate
from document_templates.service import TemplateService
from therapy_sessions.prompts import (
    SUMMARY_PROMPT,
    SYSTEM_PROMPT_SUMMARY,
    SYSTEM_PROMPT,  # Fallback
)
import logging

logger = logging.getLogger(__name__)


class SessionService:
    """Service for session-specific notes generation"""

    def __init__(self):
        self.llm_connector = get_llm_connector()
        self.template_service = TemplateService()
        self.unified_input_service = UnifiedInputService()

    def is_available(self) -> bool:
        """Check if LLM service is available"""
        return self.llm_connector.is_available()

    def reinitialize(self):
        """Reinitialize the connector (useful after settings change)"""
        self.llm_connector.reinitialize()

    def get_template(self, template_id: int, user=None) -> DocumentTemplate:
        """
        Get and validate template access for session notes

        Args:
            template_id: ID of the template
            user: User object for access validation

        Returns:
            DocumentTemplate instance

        Raises:
            DocumentTemplate.DoesNotExist: If template not found or access denied
        """
        query = DocumentTemplate.objects.filter(
            id=template_id,
            template_type=DocumentTemplate.TemplateType.SESSION_NOTES,
            is_active=True,
        )

        if user:
            query = query.filter(Q(is_predefined=True) | Q(user=user))
        else:
            query = query.filter(is_predefined=True)

        return query.get()

    def summarize_session_notes(self, session_notes: str) -> str:
        """Create ultra-short summary using LLM"""
        if not session_notes.strip():
            return ""

        prompt = SUMMARY_PROMPT.format(session_notes=session_notes)
        params = LLMGenerationParams(max_tokens=100)
        result = self.llm_connector.generate_text(SYSTEM_PROMPT_SUMMARY, prompt, params)
        return result.text

    def _build_context_prefix(self, session, existing_notes: str = None) -> str:
        """
        Build the context prefix from unified inputs

        Args:
            session: The session to build context for
            existing_notes: Existing session notes (if any)

        Returns:
            Formatted context prefix
        """
        # Use unified input service to get combined text
        combined_text = self.unified_input_service.get_combined_text(session)

        # Start building the context prefix
        context_prefix = """Erstelle strukturierte Sitzungsnotizen basierend auf dem folgenden Transkript einer Therapiesitzung.

Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

"""

        # Add patient gender context if provided
        gender_context = build_gender_context(session.patient_gender)
        if gender_context:
            context_prefix += gender_context

        if not combined_text.strip():
            context_prefix += """**HINWEIS:** Keine Kontextdateien verfügbar. Erstelle generische Sitzungsnotizen basierend auf der Vorlage.

"""
            return context_prefix

        # Format combined input text
        context_prefix += f"""**SITZUNGSINFORMATIONEN**

{combined_text}

"""

        # Include existing notes if they exist
        if existing_notes and existing_notes.strip():
            context_prefix += f"""**VORHANDENE NOTIZEN**
Die folgenden Notizen existieren bereits für diese Sitzung. Bitte berücksichtige diese und
erweitere sie sinnvoll mit den Informationen aus den Sitzungsinformationen, wo es angemessen ist.
Füge keine neuen Abschnitte hinzu:
1. Entweder erweitere die bestehenden Abschnitte wenn das neue Format mit dem vorhandenen Format kompatibel ist.
2. Oder ersetze die bestehenden Abschnitte mit dem neuen Format, schau dir aber den Inhalt an und übertrage
wenn es sinnvoll ist.

{existing_notes}

"""

        context_prefix += """Verwende diese Informationen aus den Eingaben, um strukturierte und professionelle Sitzungsnotizen zu erstellen.

**SITZUNGSNOTIZEN**

"""
        return context_prefix

    def generate_with_template(
        self, session, template: DocumentTemplate, existing_notes: str = None
    ) -> str:
        """
        Generate session notes using a specific template

        Args:
            session: The session to generate notes for
            template: The template to use
            existing_notes: Existing session notes (if any)

        Returns:
            Generated session notes
        """
        if not self.is_available():
            raise ValueError("LLM connector ist nicht verfügbar")

        try:
            context_prefix = self._build_context_prefix(session, existing_notes)

            # Combine context prefix with template structure
            full_prompt = context_prefix + template.user_prompt

            # Generate the notes using LLM connector
            params = LLMGenerationParams(
                max_tokens=template.max_tokens,
                temperature=template.temperature,
            )

            result = self.llm_connector.generate_text(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=full_prompt,
                params=params,
            )

            return result.text

        except Exception as e:
            raise Exception(f"Fehler bei der Erstellung der Sitzungsnotizen: {str(e)}")

    def generate(
        self, session, template_id: Optional[int] = None, existing_notes: str = None
    ) -> str:
        """
        Generate session notes

        Args:
            session: The session to generate notes for
            template_id: Optional specific template ID to use
            existing_notes: Existing session notes (if any)

        Returns:
            Generated session notes
        """
        if template_id:
            template = DocumentTemplate.objects.get(id=template_id)
        else:
            template = self.template_service.get_default_template(
                DocumentTemplate.TemplateType.SESSION_NOTES
            )

        if not template:
            raise ValueError("Kein Template gefunden")

        return self.generate_with_template(session, template, existing_notes)

    def get_context_summary(self, session):
        """
        Get a summary of unified inputs for a session

        Args:
            session: The session to get context summary for

        Returns:
            Dictionary with context summary
        """
        audio_inputs = session.audio_inputs.all()
        document_inputs = session.document_inputs.all()

        summary = {
            "audio_inputs": audio_inputs.count(),
            "document_inputs": document_inputs.count(),
            "total_inputs": audio_inputs.count() + document_inputs.count(),
            "successful_audio": audio_inputs.filter(processing_successful=True).count(),
            "successful_documents": document_inputs.filter(processing_successful=True).count(),
            "failed_audio": audio_inputs.filter(processing_successful=False).count(),
            "failed_documents": document_inputs.filter(processing_successful=False).count(),
            "total_text_length": (
                sum(len(ai.transcribed_text) for ai in audio_inputs if ai.transcribed_text)
                + sum(len(di.extracted_text) for di in document_inputs if di.extracted_text)
            ),
        }

        return summary

    # Legacy method for backwards compatibility - deprecated
    def create_session_notes_with_template(
        self, transcript_text: str, template, existing_notes: str = None, patient_gender: str = None
    ) -> str:
        """
        DEPRECATED: Use generate_with_template instead
        Legacy method for backwards compatibility
        """
        logger.warning(
            "create_session_notes_with_template is deprecated, use generate_with_template instead"
        )

        # This is a temporary bridge - in a real refactor, views should be updated
        # For now, we'll create a minimal session-like object
        class LegacySessionAdapter:
            def __init__(self, transcript_text, patient_gender):
                self.patient_gender = patient_gender
                self._transcript_text = transcript_text

            @property
            def audio_inputs(self):
                class MockQuerySet:
                    def all(self):
                        return []

                return MockQuerySet()

            @property
            def document_inputs(self):
                class MockQuerySet:
                    def all(self):
                        return []

                return MockQuerySet()

        # Override the unified input service method for this legacy case
        original_get_combined_text = self.unified_input_service.get_combined_text

        def mock_get_combined_text(session, include_audio=True, include_documents=True):
            return session._transcript_text if hasattr(session, "_transcript_text") else ""

        self.unified_input_service.get_combined_text = mock_get_combined_text

        try:
            session_adapter = LegacySessionAdapter(transcript_text, patient_gender)
            result = self.generate_with_template(session_adapter, template, existing_notes)
            return result
        finally:
            # Restore original method
            self.unified_input_service.get_combined_text = original_get_combined_text


# Singleton instance - lazy initialization
_session_service_instance = None


def get_session_service():
    """Get singleton session service instance"""
    global _session_service_instance
    if _session_service_instance is None:
        _session_service_instance = SessionService()
    return _session_service_instance
