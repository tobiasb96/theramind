from celery import shared_task
from .services import ReportService


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_report_content_task(self, report_id, template_id, user_id=None):
    """
    Celery task to generate report content in the background
    
    Args:
        report_id: ID of the Report instance to generate content for
        template_id: ID of the DocumentTemplate to use
        user_id: ID of the user (for template access validation)
    """
    service = ReportService()
    return service.generate(report_id, template_id, user_id)
