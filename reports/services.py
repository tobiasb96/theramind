from typing import Dict, Any, Optional
from core.connector import get_llm_connector
from core.utils.text_extraction import TextExtractionService
from document_templates.models import DocumentTemplate
from document_templates.service import TemplateService
from .models import Report
from .prompts import REPORT_SYSTEM_PROMPT
import logging

logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating therapy reports using AI"""

    def __init__(self):
        self.connector = get_llm_connector()
        self.template_service = TemplateService()
        self.text_extraction_service = TextExtractionService()

    def is_available(self) -> bool:
        """Check if the report service is available"""
        return self.connector.is_available()

    def _build_context_prefix(self, report: Report) -> str:
        """
        Build the context prefix from report context files
        
        Args:
            report: The report to build context for
            
        Returns:
            Formatted context prefix
        """
        context_files = report.context_files.filter(extraction_successful=True)

        # Start building the context prefix
        context_prefix = """Erstelle einen professionellen Bericht für eine Psychotherapie.

Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

"""

        # Add patient gender context if provided
        if report.patient_gender and report.patient_gender != "not_specified":
            gender_mapping = {"male": "männlich", "female": "weiblich", "diverse": "divers"}
            gender_display = gender_mapping.get(report.patient_gender, "nicht angegeben")

            pronouns_mapping = {
                "male": "er/ihm/sein",
                "female": "sie/ihr/ihre",
                "diverse": "sie/dey/deren (verwende geschlechtsneutrale Sprache)",
            }
            pronouns = pronouns_mapping.get(report.patient_gender, "")

            context_prefix += f"""**PATIENT*INNEN-INFORMATIONEN**
Das Geschlecht des Patienten ist {gender_display}. Verwende entsprechende Pronomen ({pronouns}) und 
geschlechtsangemessene Sprache im Bericht. Achte auf eine respektvolle und professionelle Darstellung.

"""

        if not context_files.exists():
            context_prefix += """**HINWEIS:** Keine Kontextdateien verfügbar. Erstelle einen generischen Bericht basierend auf der Vorlage.

"""
            return context_prefix
        
        # Format context files
        context_text = "**KONTEXT-INFORMATIONEN**\n\n"
        
        for context_file in context_files:
            context_text += f"**{context_file.file_name}** ({context_file.get_file_type_display()})\n"
            context_text += f"{context_file.extracted_text}\n\n"
            context_text += "---\n\n"

        context_prefix += f"""{context_text}

Verwende diese Informationen aus den Kontextdateien, um einen strukturierten und professionellen Bericht zu erstellen.

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
            raise ValueError("OpenAI API key ist nicht konfiguriert")

        try:
            context_prefix = self._build_context_prefix(report)
            
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

    def generate(self, report: Report, template_id: Optional[int] = None) -> str:
        """
        Generate a report
        
        Args:
            report: The report to generate content for
            template_id: Optional specific template ID to use
            
        Returns:
            Generated document content
        """
        if template_id:
            template = DocumentTemplate.objects.get(id=template_id)
        else:
            # TODO: Pass user_id when user model is implemented
            template = self.template_service.get_default_template(
                DocumentTemplate.TemplateType.REPORT
            )

        if not template:
            raise ValueError("Kein Template gefunden")

        return self.generate_with_template(report, template)

    def get_context_summary(self, report: Report) -> Dict[str, Any]:
        """
        Get a summary of context files for a report
        
        Args:
            report: The report to get context summary for
            
        Returns:
            Dictionary with context summary
        """
        context_files = report.context_files.all()
        
        summary = {
            'total_files': context_files.count(),
            'successful_extractions': context_files.filter(extraction_successful=True).count(),
            'failed_extractions': context_files.filter(extraction_successful=False).count(),
            'total_text_length': sum(len(cf.extracted_text) for cf in context_files if cf.extracted_text),
            'file_types': {},
        }
        
        # Count file types
        for file_type in ReportContextFile.FileType:
            count = context_files.filter(file_type=file_type.value).count()
            if count > 0:
                summary['file_types'][file_type.label] = count
        
        return summary