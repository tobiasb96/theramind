from typing import Optional
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
        context_prefix = ""

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
            full_prompt = f"""
            **AUFGABE** 
            Erstelle strukturierte Sitzungsnotizen basierend auf Informationen zu einer Therapiesitzung.
            
        
            **ALLGEMEINE ANWEISUNGEN FÜR DIE ERSTELLUNG DER SITZUNGSNOTIZEN**
            {template.general_instructions}
            
            
            **STRUKTUR FÜR DIE ERSTELLUNG DER SITZUNGSNOTIZEN**
            {template.user_prompt}
            
        
            {context_prefix}
        
            
            **ANTWORTFORMAT**
            Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>
            """

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
        self,
        session_id: int,
        template_id: int,
        user_id: Optional[int] = None,
        existing_notes: str = None,
    ):
        """
        Generate session notes for background tasks

        Args:
            session_id: ID of the Session instance
            template_id: ID of the DocumentTemplate to use
            user_id: ID of the user for template access validation
            existing_notes: Existing session notes (if any)

        Returns:
            Task result dictionary
        """
        from django.core.exceptions import ObjectDoesNotExist
        from .models import Session

        try:
            session = Session.objects.get(id=session_id)
        except ObjectDoesNotExist:
            logger.error(f"Session with id {session_id} not found")
            return {"success": False, "error": "Session not found"}

        # Mark as generating at the start
        session.mark_as_generating()

        try:
            logger.info(
                f"Starting session notes generation for Session {session_id} ({session.title})"
            )

            # Get user for template validation if provided
            user = None
            if user_id:
                from django.contrib.auth import get_user_model

                User = get_user_model()
                try:
                    user = User.objects.get(id=user_id)
                except ObjectDoesNotExist:
                    logger.warning(
                        f"User with id {user_id} not found, proceeding without user context"
                    )

            # Validate service availability
            if not self.is_available():
                raise ValueError("LLM connector ist nicht verfügbar")

            # Validate template access
            try:
                template = DocumentTemplate.objects.get_template(
                    int(template_id), DocumentTemplate.TemplateType.SESSION_NOTES, user=user
                )
            except Exception as e:
                raise ValueError(f"Template nicht gefunden: {str(e)}")

            # Generate session notes
            session_notes = self.generate_with_template(session, template, existing_notes)

            # Generate summary if notes were created
            summary = None
            if session_notes:
                try:
                    summary = self.summarize_session_notes(session_notes)
                except Exception as e:
                    logger.error(f"Fehler bei der Zusammenfassung: {str(e)}")

            # Update session with generated content and mark as successful
            session.notes = session_notes
            if summary:
                session.summary = summary
            session.mark_as_success()

            logger.info(f"Session notes generation completed successfully for Session {session_id}")

            return {
                "success": True,
                "session_id": session_id,
                "notes_length": len(session_notes) if session_notes else 0,
                "has_summary": bool(summary),
            }

        except Exception as exc:
            logger.error(f"Error generating session notes for Session {session_id}: {str(exc)}")
            session.mark_as_failed()
            return {"success": False, "error": str(exc)}

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


# Singleton instance - lazy initialization
_session_service_instance = None


def get_session_service():
    """Get singleton session service instance"""
    global _session_service_instance
    if _session_service_instance is None:
        _session_service_instance = SessionService()
    return _session_service_instance
