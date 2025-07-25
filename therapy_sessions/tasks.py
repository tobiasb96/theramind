from celery import shared_task
from .services import get_session_service


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_session_notes_task(self, session_id, template_id, user_id=None, existing_notes=None):
    """
    Celery task to generate session notes in the background
    
    Args:
        session_id: ID of the Session instance to generate notes for
        template_id: ID of the DocumentTemplate to use
        user_id: ID of the user (for template access validation)
        existing_notes: Existing session notes (if any)
    """
    session_service = get_session_service()
    return session_service.generate(session_id, template_id, user_id, existing_notes)
