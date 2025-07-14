from typing import Dict, Any, List
from django.db.models import Q
from core.connector import get_llm_connector
from .models import DocumentTemplate, UserTemplatePreference
from .prompts import DOCUMENT_SYSTEM_PROMPT
from patients.models import Patient
from therapy.models import Therapy


class TemplateService:
    """Service for managing custom templates"""

    def __init__(self):
        self.connector = get_llm_connector()

    def is_available(self) -> bool:
        """Check if the template service is available"""
        return self.connector.is_available()

    def get_available_templates(self, template_type: str, user_id=None) -> List[DocumentTemplate]:
        """
        Get available templates for a specific type and user

        Args:
            template_type: 'document' or 'session_notes'
            user_id: User ID (TODO: implement when user model is ready)

        Returns:
            List of available templates
        """
        # Get predefined templates
        predefined_templates = DocumentTemplate.objects.filter(
            template_type=template_type, is_predefined=True, is_active=True
        )

        # TODO: Add user-specific templates when user model is implemented
        # if user_id:
        #     user_templates = DocumentTemplate.objects.filter(
        #         template_type=template_type,
        #         user_id=user_id,
        #         is_active=True
        #     )
        #     return list(predefined_templates) + list(user_templates)

        return list(predefined_templates)

    def get_document_templates(
        self, document_type: str = None, user_id=None
    ) -> List[DocumentTemplate]:
        """Get document templates, optionally filtered by document type"""
        templates = self.get_available_templates("document", user_id)

        if document_type:
            templates = [t for t in templates if t.document_type == document_type]

        return templates

    def get_session_templates(self, user_id=None) -> List[DocumentTemplate]:
        """Get session notes templates"""
        return self.get_available_templates("session_notes", user_id)

    def create_custom_template(
        self, template_data: Dict[str, Any], user_id=None
    ) -> DocumentTemplate:
        """
        Create a custom template

        Args:
            template_data: Template data dictionary
            user_id: User ID (TODO: implement when user model is ready)

        Returns:
            Created template
        """
        # TODO: Add user validation when user model is implemented
        # if user_id:
        #     template_data['user_id'] = user_id

        template = DocumentTemplate.objects.create(**template_data)
        return template

    def clone_template(self, template_id: int, new_name: str, user_id=None) -> DocumentTemplate:
        """
        Clone an existing template for customization

        Args:
            template_id: ID of template to clone
            new_name: Name for the new template
            user_id: User ID (TODO: implement when user model is ready)

        Returns:
            Cloned template
        """
        original_template = DocumentTemplate.objects.get(id=template_id)

        cloned_template = DocumentTemplate.objects.create(
            name=new_name,
            description=f"Basiert auf {original_template.name}",
            template_type=original_template.template_type,
            document_type=original_template.document_type,
            system_prompt=original_template.system_prompt,
            user_prompt=original_template.user_prompt,
            max_tokens=original_template.max_tokens,
            temperature=original_template.temperature,
            is_predefined=False,
            is_active=True,
            based_on_template=original_template,
            # TODO: Add user when user model is implemented
            # user_id=user_id
        )

        return cloned_template

    def get_default_template(
        self, template_type: str, document_type: str = None, user_id=None
    ) -> DocumentTemplate:
        """
        Get the default template for a specific type

        Args:
            template_type: 'document' or 'session_notes'
            document_type: Document type (for document templates)
            user_id: User ID (TODO: implement when user model is ready)

        Returns:
            Default template
        """
        # TODO: Check user preferences when user model is implemented
        # if user_id:
        #     try:
        #         preferences = UserTemplatePreference.objects.get(user_id=user_id)
        #         if template_type == 'document' and document_type:
        #             template_id = preferences.default_document_templates.get(document_type)
        #             if template_id:
        #                 return DocumentTemplate.objects.get(id=template_id)
        #         elif template_type == 'session_notes':
        #             template_id = preferences.default_session_templates.get('default')
        #             if template_id:
        #                 return DocumentTemplate.objects.get(id=template_id)
        #     except (UserTemplatePreference.DoesNotExist, DocumentTemplate.DoesNotExist):
        #         pass

        # Fall back to first predefined template
        return DocumentTemplate.objects.filter(
            template_type=template_type,
            document_type=document_type if template_type == "document" else None,
            is_predefined=True,
            is_active=True,
        ).first()


class DocumentService:
    """Service for generating therapy documents using AI"""

    def __init__(self):
        self.connector = get_llm_connector()
        self.template_service = TemplateService()

    def is_available(self) -> bool:
        """Check if the document service is available"""
        return self.connector.is_available()

    def _build_context_prefix(self, patient: Patient, therapy: Therapy) -> str:
        """
        Build the context prefix with patient and therapy information

        Args:
            patient: The patient
            therapy: The therapy

        Returns:
            Formatted context prefix
        """
        # Prepare context data
        context_data = self._prepare_context_data(patient, therapy)

        # Build the context prefix
        context_prefix = f"""Erstelle ein professionelles Dokument für eine Psychotherapie.

Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

**PATIENTENINFORMATIONEN**
- Alter: {context_data["patient_info"]["age"]}
- Geschlecht: {context_data["patient_info"]["gender"]}
- Beruf: {context_data["patient_info"]["occupation"]}
- Familienstand: {context_data["patient_info"]["marital_status"]}

**THERAPIEINFORMATIONEN**
- Therapiebeginn: {context_data["therapy_info"]["start_date"]}
- Therapieende: {context_data["therapy_info"]["end_date"]}
- Anzahl Sitzungen: {context_data["therapy_info"]["session_count"]}
- Therapieziele: {context_data["therapy_info"]["goals"]}

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

    def generate_with_template(
        self, patient: Patient, therapy: Therapy, template: DocumentTemplate
    ) -> str:
        """
        Generate a document using a specific template

        Args:
            patient: The patient for whom to generate the document
            therapy: The therapy context
            template: The template to use

        Returns:
            Generated document content
        """
        if not self.is_available():
            raise ValueError("OpenAI API key ist nicht konfiguriert")

        try:
            # Build context prefix with patient/therapy info
            context_prefix = self._build_context_prefix(patient, therapy)

            # Combine context prefix with template structure
            full_prompt = context_prefix + template.user_prompt

            # Generate the document using hardcoded system prompt
            return self.connector.generate_text(
                system_prompt=DOCUMENT_SYSTEM_PROMPT,
                user_prompt=full_prompt,
                max_tokens=template.max_tokens,
                temperature=template.temperature,
            )

        except Exception as e:
            raise Exception(f"Fehler bei der Dokumentgenerierung: {str(e)}")

    def generate(
        self, patient: Patient, therapy: Therapy, document_type: str, template_id: int = None
    ) -> str:
        """
        Generate a document of the specified type for a patient and therapy

        Args:
            patient: The patient for whom to generate the document
            therapy: The therapy context
            document_type: Type of document to generate (e.g., 'abschlussbericht')
            template_id: Optional specific template ID to use

        Returns:
            Generated document content
        """
        if template_id:
            template = DocumentTemplate.objects.get(id=template_id)
        else:
            # TODO: Pass user_id when user model is implemented
            template = self.template_service.get_default_template("document", document_type)

        if not template:
            raise ValueError(f"Kein Template für Dokumenttyp {document_type} gefunden")

        return self.generate_with_template(patient, therapy, template)

    def _prepare_context_data(self, patient: Patient, therapy: Therapy) -> Dict[str, Any]:
        """
        Prepare context data for document generation
        
        Args:
            patient: The patient
            therapy: The therapy
            
        Returns:
            Dictionary with context data
        """
        # Get all sessions for this therapy
        sessions = therapy.session_set.order_by('date')
        
        # Get all transcriptions for this therapy
        transcriptions = []
        for session in sessions:
            for recording in session.audiorecording_set.all():
                if hasattr(recording, 'transcription') and recording.transcription:
                    transcriptions.append({
                        'session_date': session.date.strftime('%d.%m.%Y'),
                        'session_title': session.title or f"Sitzung vom {session.date.strftime('%d.%m.%Y')}",
                        'text': recording.transcription.text,
                        'summary': session.summary or "Keine Zusammenfassung verfügbar"
                    })
        
        # Prepare patient information (anonymized)
        patient_info = {
            'age': patient.age if hasattr(patient, 'age') else "Nicht angegeben",
            'gender': patient.gender if hasattr(patient, 'gender') else "Nicht angegeben",
            'occupation': getattr(patient, 'occupation', 'Nicht angegeben'),
            'marital_status': getattr(patient, 'marital_status', 'Nicht angegeben'),
        }
        
        # Prepare therapy information
        therapy_info = {
            'start_date': therapy.start_date.strftime('%d.%m.%Y'),
            'end_date': therapy.end_date.strftime('%d.%m.%Y') if therapy.end_date else "Laufend",
            'status': therapy.get_status_display(),
            'goals': therapy.goals or "Keine Ziele definiert",
            'notes': therapy.notes or "Keine Notizen verfügbar",
            'session_count': sessions.count(),
        }
        
        return {
            'patient_info': patient_info,
            'therapy_info': therapy_info,
            'sessions': sessions,
            'transcriptions': transcriptions,
            'patient': patient,
            'therapy': therapy,
        } 