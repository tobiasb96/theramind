from typing import Dict, Any, List
from core.connector import get_llm_connector
from document_templates.service import TemplateService
from .models import DocumentTemplate
from .prompts import REPORT_SYSTEM_PROMPT


class ReportService:
    """Service for generating therapy reports using AI"""

    def __init__(self):
        self.connector = get_llm_connector()
        self.template_service = TemplateService()

    def is_available(self) -> bool:
        """Check if the report service is available"""
        return self.connector.is_available()

    def _build_context_prefix(self) -> str:
        """
        Build the context prefix

        Returns:
            Formatted context prefix
        """
        # Prepare context data
        context_data = self._prepare_context_data()

        # Build the context prefix
        context_prefix = f"""Erstelle ein professionelles Dokument für eine Psychotherapie.

            Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

            **THERAPIEVERLAUF**
            {self._format_transcriptions(context_data["transcriptions"])}

"""
        return context_prefix

    def _format_transcriptions(self, transcriptions: List[Dict[str, Any]]) -> str:
        """Format transcriptions for inclusion in prompts"""
        if not transcriptions:
            return "Keine Transkriptionen verfügbar"

        formatted = []
        for t in transcriptions:
            formatted.append(
                f"**{t['session_title']}**\n{t['text']}\n\nZusammenfassung: {t['summary']}"
            )

        return "\n\n".join(formatted)

    def generate_with_template(self, template: DocumentTemplate) -> str:
        """
        Generate a report using a specific template

        Args:
            template: The template to use

        Returns:
            Generated report content
        """
        if not self.is_available():
            raise ValueError("OpenAI API key ist nicht konfiguriert")

        try:
            context_prefix = self._build_context_prefix()

            # Combine context prefix with template structure
            full_prompt = context_prefix + template.user_prompt

            # Generate the document using hardcoded system prompt
            return self.connector.generate_text(
                system_prompt=REPORT_SYSTEM_PROMPT,
                user_prompt=full_prompt,
                max_tokens=template.max_tokens,
                temperature=template.temperature,
            )

        except Exception as e:
            raise Exception(f"Fehler bei der Reportgenerierung: {str(e)}")

    def generate(self, template_id: int = None) -> str:
        """
        Generate a report

        Args:
            template_id: Optional specific template ID to use

        Returns:
            Generated document content
        """
        if template_id:
            template = DocumentTemplate.objects.get(id=template_id)
        else:
            # TODO: Pass user_id when user model is implemented
            template = self.template_service.get_default_template("document")

        if not template:
            raise ValueError("Kein Template gefunden")

        return self.generate_with_template(template)

    def _prepare_context_data(self) -> Dict[str, Any]:
        """
        Prepare context data for report generation

        Returns:
            Dictionary with context data
        """
        return {}