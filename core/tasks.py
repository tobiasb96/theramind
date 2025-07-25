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
    
    try:
        logger.info(f"Starting audio transcription for AudioInput {audio_input_id} ({audio_input.name})")
        service = UnifiedInputService()
        service._process_audio_transcription(audio_input, therapeutic_observations)
        logger.info(f"Audio transcription completed for AudioInput {audio_input_id} with result: {audio_input.processing_successful}")
        
        return {
            "success": True, 
            "audio_input_id": audio_input_id,
            "processing_successful": audio_input.processing_successful,
            "error": audio_input.processing_error if not audio_input.processing_successful else None
        }
        
    except Exception as exc:
        logger.error(f"Error processing audio transcription for AudioInput {audio_input_id}: {str(exc)}")
        audio_input.mark_as_failed(str(exc))    
        return {"success": False, "error": str(exc)}


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
    
    try:
        logger.info(f"Starting document extraction for DocumentInput {document_input_id} ({document_input.name})")
        service = UnifiedInputService()
        service._process_document_extraction(document_input)
        logger.info(f"Document extraction completed for DocumentInput {document_input_id} with result: {document_input.processing_successful}")
        return {
            "success": True,
            "document_input_id": document_input_id,
            "processing_successful": document_input.processing_successful,
            "error": document_input.processing_error if not document_input.processing_successful else None
        }
        
    except Exception as exc:
        logger.error(f"Error processing document extraction for DocumentInput {document_input_id}: {str(exc)}")
        document_input.mark_as_failed(str(exc))
        return {"success": False, "error": str(exc)}
