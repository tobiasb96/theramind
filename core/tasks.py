import logging
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from core.services import UnifiedInputService
from core.models import DocumentInput, AudioInput

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_audio_transcription_task(self, audio_input_id, therapeutic_observations=""):
    """Process audio transcription in the background"""
    try:
        audio_input = AudioInput.objects.get(id=audio_input_id)
        service = UnifiedInputService()
        service.process_audio_transcription(audio_input, therapeutic_observations)
        return {"success": True, "audio_input_id": audio_input_id}
    except ObjectDoesNotExist:
        logger.error(f"AudioInput {audio_input_id} not found")
        return {"success": False, "error": "AudioInput not found"}
    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60)
        logger.error(f"Audio transcription failed for {audio_input_id}: {exc}")
        return {"success": False, "error": str(exc)}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_extraction_task(self, document_input_id):
    """Process document text extraction in the background"""
    try:
        document_input = DocumentInput.objects.get(id=document_input_id)
        service = UnifiedInputService()
        service.process_document_extraction(document_input)
        return {"success": True, "document_input_id": document_input_id}
    except ObjectDoesNotExist:
        logger.error(f"DocumentInput {document_input_id} not found")
        return {"success": False, "error": "DocumentInput not found"}
    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60)
        logger.error(f"Document extraction failed for {document_input_id}: {exc}")
        return {"success": False, "error": str(exc)}
