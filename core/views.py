from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
import logging

from .models import AudioInput, DocumentInput
from .services import UnifiedInputService
from therapy_sessions.models import Session
from reports.models import Report

logger = logging.getLogger(__name__)


class UnifiedInputViewSet(viewsets.ViewSet):
    """Unified viewset for handling both audio and document inputs"""
    
    permission_classes = [IsAuthenticated]
    
    def get_document(self, document_type, document_id, request):
        """Get document with security check"""
        if document_type == 'session':
            return get_object_or_404(Session, pk=document_id, user=request.user)
        elif document_type == 'report':
            return get_object_or_404(Report, pk=document_id, user=request.user)
        else:
            raise Http404("Invalid document type")
    
    @action(detail=False, methods=['post'])
    @method_decorator(csrf_exempt)
    def add_audio(self, request, document_type=None, document_id=None):
        """Add audio input (recording or upload)"""
        document = self.get_document(document_type, document_id, request)
        
        if 'audio_file' not in request.FILES:
            messages.error(request, "Keine Audio-Datei hochgeladen")
            return redirect(f"{document_type}s:{document_type}_detail", pk=document.pk)
        
        try:
            service = UnifiedInputService()
            audio_input = service.add_audio_input(
                document=document,
                audio_file=request.FILES['audio_file'],
                audio_type=request.POST.get('audio_type', 'upload'),
                therapeutic_observations=request.POST.get('therapeutic_observations', '')
            )
            
            if audio_input.processing_successful:
                messages.success(request, f"Audio '{audio_input.name}' wurde erfolgreich hinzugefügt und verarbeitet.")
            else:
                messages.warning(request, f"Audio '{audio_input.name}' wurde hinzugefügt, aber die Verarbeitung fehlgeschlagen: {audio_input.processing_error}")
            
        except Exception as e:
            logger.error(f"Error adding audio input: {str(e)}")
            messages.error(request, f"Fehler beim Hinzufügen der Audio-Datei: {str(e)}")
        
        return redirect(f"{document_type}s:{document_type}_detail", pk=document.pk)
    
    @action(detail=False, methods=['post'])
    @method_decorator(csrf_exempt)
    def add_document_file(self, request, document_type=None, document_id=None):
        """Add document file input"""
        document = self.get_document(document_type, document_id, request)
        
        if 'document_file' not in request.FILES:
            messages.error(request, "Keine Datei hochgeladen")
            return redirect(f"{document_type}s:{document_type}_detail", pk=document.pk)
        
        try:
            service = UnifiedInputService()
            document_input = service.add_document_input(
                document=document,
                file=request.FILES['document_file']
            )
            
            if document_input.processing_successful:
                messages.success(request, f"Dokument '{document_input.name}' wurde erfolgreich hinzugefügt und verarbeitet.")
            else:
                messages.warning(request, f"Dokument '{document_input.name}' wurde hinzugefügt, aber die Verarbeitung fehlgeschlagen: {document_input.processing_error}")
            
        except Exception as e:
            logger.error(f"Error adding document file: {str(e)}")
            messages.error(request, f"Fehler beim Hinzufügen der Datei: {str(e)}")
        
        return redirect(f"{document_type}s:{document_type}_detail", pk=document.pk)
    
    @action(detail=False, methods=['post'])
    @method_decorator(csrf_exempt)
    def add_document_text(self, request, document_type=None, document_id=None):
        """Add manual text input"""
        document = self.get_document(document_type, document_id, request)
        
        text_content = request.POST.get('text_content', '').strip()
        if not text_content:
            messages.error(request, "Kein Text eingegeben")
            return redirect(f"{document_type}s:{document_type}_detail", pk=document.pk)
        
        try:
            service = UnifiedInputService()
            document_input = service.add_document_input(
                document=document,
                text=text_content
            )
            
            messages.success(request, f"Text '{document_input.name}' wurde erfolgreich hinzugefügt.")
            
        except Exception as e:
            logger.error(f"Error adding document text: {str(e)}")
            messages.error(request, f"Fehler beim Hinzufügen des Texts: {str(e)}")
        
        return redirect(f"{document_type}s:{document_type}_detail", pk=document.pk)
    
    @action(detail=True, methods=['post'])
    @method_decorator(csrf_exempt)
    def delete_audio(self, request, pk=None):
        """Delete an audio input"""
        # Get the audio input first
        audio_input = get_object_or_404(AudioInput, pk=pk)

        # Get the associated document
        document = audio_input.document

        # Security check: ensure the document belongs to the user
        if not hasattr(document, "user") or document.user != request.user:
            raise Http404("Audio input not found")
        
        try:
            input_name = audio_input.name
            document_type = 'session' if isinstance(document, Session) else 'report'
            document_id = document.pk
            
            audio_input.delete()
            messages.success(request, f"Audio '{input_name}' wurde erfolgreich gelöscht.")
            
        except Exception as e:
            logger.error(f"Error deleting audio input: {str(e)}")
            messages.error(request, f"Fehler beim Löschen: {str(e)}")
        
        return redirect(f"{document_type}s:{document_type}_detail", pk=document_id)
    
    @action(detail=True, methods=['post'])
    @method_decorator(csrf_exempt)
    def delete_document(self, request, pk=None):
        """Delete a document input"""
        # Get the document input first
        document_input = get_object_or_404(DocumentInput, pk=pk)

        # Get the associated document
        document = document_input.document

        # Security check: ensure the document belongs to the user
        if not hasattr(document, "user") or document.user != request.user:
            raise Http404("Document input not found")
        
        try:
            input_name = document_input.name
            document_type = 'session' if isinstance(document, Session) else 'report'
            document_id = document.pk
            
            document_input.delete()
            messages.success(request, f"Dokument '{input_name}' wurde erfolgreich gelöscht.")
            
        except Exception as e:
            logger.error(f"Error deleting document input: {str(e)}")
            messages.error(request, f"Fehler beim Löschen: {str(e)}")
        
        return redirect(f"{document_type}s:{document_type}_detail", pk=document_id) 