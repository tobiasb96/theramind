from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model
from core.ai_connectors import get_llm_connector
from core.ai_connectors.base.llm import LLMGenerationParams
from core.utils.ai_helpers import build_gender_context
from core.services import UnifiedInputService
from document_templates.models import DocumentTemplate
from document_templates.service import TemplateService
from .models import Report
from .prompts import REPORT_SYSTEM_PROMPT
import logging

logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating therapy reports using AI"""

    def __init__(self):
        self.llm_connector = get_llm_connector()
        self.template_service = TemplateService()
        self.unified_input_service = UnifiedInputService()

    def is_available(self) -> bool:
        """Check if the report service is available"""
        return self.llm_connector.is_available()

    def reinitialize(self):
        """Reinitialize the connector (useful after settings change)"""
        self.llm_connector.reinitialize()

    def _build_context_prefix(self, report: Report) -> str:
        """
        Build the context prefix from unified inputs

        Args:
            report: The report to build context for

        Returns:
            Formatted context prefix
        """
        # Use unified input service to get combined text
        combined_text = self.unified_input_service.get_combined_text(report)

        # Start building the context prefix
        context_prefix = """Erstelle einen professionellen Bericht für eine Psychotherapie.

Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

"""

        # Add patient gender context if provided
        gender_context = build_gender_context(report.patient_gender)
        if gender_context:
            context_prefix += gender_context

        if not combined_text.strip():
            context_prefix += """**HINWEIS:** Keine Kontextdateien verfügbar. Erstelle einen generischen Bericht basierend auf der Vorlage.

"""
            return context_prefix

        # Format combined input text
        context_prefix += f"""**KONTEXT-INFORMATIONEN**

{combined_text}

Verwende diese Informationen aus den Eingaben, um einen strukturierten und professionellen Bericht zu erstellen.

"""
        return context_prefix

    def generate_with_template(self, report: Report, template: DocumentTemplate) -> str:
        """
        Generate a report using a specific template

        Args:
            report: The report to generate content for
            template: The template to use

        Returns:
            Generated report content
        """
        if not self.is_available():
            raise ValueError("LLM connector ist nicht verfügbar")

        try:
            context_prefix = self._build_context_prefix(report)

            # Combine context prefix with template structure
            full_prompt = context_prefix + template.user_prompt

            # Generate the document using LLM connector
            params = LLMGenerationParams(
                max_tokens=template.max_tokens,
                temperature=template.temperature,
            )

            result = self.llm_connector.generate_text(
                system_prompt=REPORT_SYSTEM_PROMPT,
                user_prompt=full_prompt,
                params=params,
            )

            return result.text

        except Exception as e:
            raise Exception(f"Fehler bei der Reportgenerierung: {str(e)}")

    def generate(self, report_id: int, template_id: int, user_id: Optional[int] = None):
        """
        Generate a report for background tasks

        Args:
            report_id: ID of the Report instance
            template_id: ID of the DocumentTemplate to use
            user_id: ID of the user for template access validation

        Returns:
            Task result dictionary
        """
        from django.core.exceptions import ObjectDoesNotExist

        try:
            report = Report.objects.get(id=report_id)
        except ObjectDoesNotExist:
            logger.error(f"Report with id {report_id} not found")
            return {"success": False, "error": "Report not found"}

        # Mark as generating at the start
        report.mark_as_generating()

        try:
            logger.info(
                f"Starting report content generation for Report {report_id} ({report.title})"
            )

            # Get user for template validation if provided
            user = None
            if user_id:
                User = get_user_model()
                try:
                    user = User.objects.get(id=user_id)
                except ObjectDoesNotExist:
                    logger.warning(
                        f"User with id {user_id} not found, proceeding without user context"
                    )

            template = DocumentTemplate.objects.get_template(
                int(template_id), DocumentTemplate.TemplateType.REPORT, user=user
            )
            generated_content = self.generate_with_template(report, template)
            report.content = generated_content
            report.mark_as_success()

            logger.info(f"Report content generation completed successfully for Report {report_id}")

            return {
                "success": True,
                "report_id": report_id,
                "content_length": len(generated_content),
            }

        except Exception as exc:
            logger.error(f"Error generating report content for Report {report_id}: {str(exc)}")
            report.mark_as_failed()
            return {"success": False, "error": str(exc)}

    def get_context_summary(self, report: Report) -> Dict[str, Any]:
        """
        Get a summary of unified inputs for a report

        Args:
            report: The report to get context summary for

        Returns:
            Dictionary with context summary
        """
        audio_inputs = report.audio_inputs.all()
        document_inputs = report.document_inputs.all()
        
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