from typing import Dict, Any, List
from core.connector import get_llm_connector
from .models import DocumentTemplate


class TemplateService:
    """Service for managing custom templates"""

    def __init__(self):
        self.connector = get_llm_connector()

    def is_available(self) -> bool:
        """Check if the template service is available"""
        return self.connector.is_available()

    def get_available_templates(self, template_type: str, user=None) -> List[DocumentTemplate]:
        """
        Get available templates for a specific type and user

        Args:
            template_type: 'document' or 'session_notes'
            user: User object
        Returns:
            List of available templates
        """
        # Get predefined templates
        predefined_templates = DocumentTemplate.objects.filter(
            template_type=template_type, is_predefined=True, is_active=True
        )

        if user:
            from django.db.models import Q
            all_templates = DocumentTemplate.objects.filter(
                template_type=template_type,
                is_active=True
            ).filter(
                Q(is_predefined=True) | Q(user=user)
            )
            return list(all_templates)

        return list(predefined_templates)

    def get_document_templates(self, user=None) -> List[DocumentTemplate]:
        """Get document templates"""
        return self.get_available_templates("document", user)

    def get_session_templates(self, user=None) -> List[DocumentTemplate]:
        """Get session notes templates"""
        return self.get_available_templates("session_notes", user)

    def create_custom_template(
        self, template_data: Dict[str, Any], user=None
    ) -> DocumentTemplate:
        """
        Create a custom template

        Args:
            template_data: Template data dictionary
            user: User object

        Returns:
            Created template
        """
        if user:
            template_data['user'] = user

        template = DocumentTemplate.objects.create(**template_data)
        return template

    def clone_template(self, template_id: int, new_name: str, user=None) -> DocumentTemplate:
        """
        Clone an existing template for customization

        Args:
            template_id: ID of template to clone
            new_name: Name for the new template
            user: User object

        Returns:
            Cloned template
        """
        from django.db.models import Q
        original_template = DocumentTemplate.objects.filter(
            id=template_id,
            is_active=True
        ).filter(
            Q(is_predefined=True) | Q(user=user)
        ).first()
        
        if not original_template:
            raise DocumentTemplate.DoesNotExist("Template not found or access denied")

        cloned_template = DocumentTemplate.objects.create(
            name=new_name,
            description=f"Basiert auf {original_template.name}",
            template_type=original_template.template_type,
            system_prompt=original_template.system_prompt,
            user_prompt=original_template.user_prompt,
            max_tokens=original_template.max_tokens,
            temperature=original_template.temperature,
            is_predefined=False,
            is_active=True,
            based_on_template=original_template,
            user=user
        )

        return cloned_template

    def get_default_template(self, template_type: str, user=None) -> DocumentTemplate:
        """
        Get the default template for a specific type

        Args:
            template_type: 'document' or 'session_notes'
            user: User object

        Returns:
            Default template
        """
        if user:
            try:
                from .models import UserTemplatePreference
                preferences = UserTemplatePreference.objects.get(user=user)
                if template_type == 'document':
                    template_id = preferences.default_document_templates.get('default')
                    if template_id:
                        from django.db.models import Q
                        template = DocumentTemplate.objects.filter(
                            id=template_id,
                            is_active=True
                        ).filter(
                            Q(is_predefined=True) | Q(user=user)
                        ).first()
                        if template:
                            return template
                elif template_type == 'session_notes':
                    template_id = preferences.default_session_templates.get('default')
                    if template_id:
                        from django.db.models import Q
                        template = DocumentTemplate.objects.filter(
                            id=template_id,
                            is_active=True
                        ).filter(
                            Q(is_predefined=True) | Q(user=user)
                        ).first()
                        if template:
                            return template
            except (UserTemplatePreference.DoesNotExist, DocumentTemplate.DoesNotExist):
                pass

        # Fall back to first predefined template
        return DocumentTemplate.objects.filter(
            template_type=template_type,
            is_predefined=True,
            is_active=True,
        ).first()
