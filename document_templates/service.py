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

    def get_document_templates(self, user_id=None) -> List[DocumentTemplate]:
        """Get document templates"""
        return self.get_available_templates("document", user_id)

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

    def get_default_template(self, template_type: str, user_id=None) -> DocumentTemplate:
        """
        Get the default template for a specific type

        Args:
            template_type: 'document' or 'session_notes'
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
            is_predefined=True,
            is_active=True,
        ).first()
