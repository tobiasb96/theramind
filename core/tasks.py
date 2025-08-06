import logging
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from core.services import UnifiedInputService
from core.models import DocumentInput, AudioInput

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_audio_transcription_task(self, audio_input_id, therapeutic_observations=""):
    """
    Celery task to process audio transcription in the background
    
    Args:
        audio_input_id: ID of the AudioInput instance to process
        therapeutic_observations: Additional therapeutic observations to append
    """
    try:
        audio_input = AudioInput.objects.get(id=audio_input_id)
    except ObjectDoesNotExist:
        logger.error(f"AudioInput with id {audio_input_id} not found")
        return {"success": False, "error": "AudioInput not found"}

    logger.info(
        f"Starting audio transcription for AudioInput {audio_input_id} ({audio_input.name})"
    )
    
    try:
        service = UnifiedInputService()
        service.process_audio_transcription(audio_input, therapeutic_observations)
        audio_input.refresh_from_db()
        
        if audio_input.processing_successful:
            logger.info(
                f"Audio transcription completed successfully for AudioInput {audio_input_id}"
            )
            return {
                "success": True,
                "audio_input_id": audio_input_id,
                "processing_successful": audio_input.processing_successful,
            }
        else:
            # If processing failed, check if we should retry
            error_msg = f"Transcription failed for AudioInput {audio_input_id}"
            if self.request.retries < self.max_retries:
                logger.warning(f"{error_msg}. Retrying... (attempt {self.request.retries + 1}/{self.max_retries})")
                raise self.retry(countdown=60)
            else:
                # Final failure - log and return error, but keep audio file for manual inspection
                logger.error(f"{error_msg}. All retries exhausted. Audio file preserved for manual review.")
                return {
                    "success": False,
                    "audio_input_id": audio_input_id,
                    "processing_successful": False,
                    "error": "All transcription attempts failed"
                }
    except Exception as exc:
        # Unexpected error during transcription processing
        error_msg = f"Unexpected error processing AudioInput {audio_input_id}: {str(exc)}"
        if self.request.retries < self.max_retries:
            logger.warning(f"{error_msg}. Retrying... (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=exc, countdown=60)
        else:
            # Final failure - log and mark as failed, but keep audio file for manual inspection
            logger.error(f"{error_msg}. All retries exhausted.")
            try:
                audio_input.mark_as_failed(str(exc))
            except:
                pass  # Don't fail if we can't update the record
            return {
                "success": False,
                "audio_input_id": audio_input_id,
                "processing_successful": False,
                "error": str(exc)
            }


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_extraction_task(self, document_input_id):
    """
    Celery task to process document text extraction in the background
    
    Args:
        document_input_id: ID of the DocumentInput instance to process
    """
    try:
        document_input = DocumentInput.objects.get(id=document_input_id)
    except ObjectDoesNotExist:
        logger.error(f"DocumentInput with id {document_input_id} not found")
        return {"success": False, "error": "DocumentInput not found"}

    service = UnifiedInputService()
    service.process_document_extraction(document_input)
    document_input.refresh_from_db()
    logger.info(
        f"Document extraction completed for DocumentInput {document_input_id} with result: {document_input.processing_successful}"
    )
    return {
        "success": True,
        "document_input_id": document_input_id,
        "processing_successful": document_input.processing_successful,
    }
