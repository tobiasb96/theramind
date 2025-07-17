from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets
from rest_framework.decorators import action
import os
import logging

from therapy_sessions.models import Session, AudioRecording, Transcription
from therapy_sessions.services import get_transcription_service

logger = logging.getLogger(__name__)


class AudioViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing audio recording operations.
    """
    
    def get_queryset(self):
        return AudioRecording.objects.all().order_by('-created_at')

    def get_session(self, pk):
        """Get session with nested relationship validation"""
        return get_object_or_404(Session, pk=pk)
    
    @action(detail=False, methods=['post'])
    @method_decorator(csrf_exempt)
    def upload(self, request, pk=None):
        """Upload audio file to a session"""
        session = self.get_session(pk)
        
        if 'audio' not in request.FILES:
            if request.headers.get("HX-Request"):
                return JsonResponse({"error": "Keine Audio-Datei hochgeladen"}, status=400)
            else:
                messages.error(request, "Keine Audio-Datei hochgeladen")
                return redirect(
                    "sessions:session_detail",
                    pk=session.pk,
                )
        
        audio_file = request.FILES['audio']
        
        try:
            # Create audio recording
            recording = AudioRecording.objects.create(
                session=session, 
                audio=audio_file, 
                file_size=audio_file.size
            )

            # Auto-transcribe if enabled
            transcription_service = get_transcription_service()
            if transcription_service.is_available():
                try:
                    # Transcribe audio
                    file_path = recording.audio.path
                    transcribed_text, processing_time = transcription_service.transcribe(file_path)
                    
                    # Create transcription
                    Transcription.objects.create(
                        recording=recording,
                        text=transcribed_text,
                        processing_time_seconds=processing_time,
                    )
                    
                    recording.is_processed = True
                    recording.save()
                    
                    # Auto-summarize if enabled
                    if transcribed_text:
                        summary = transcription_service.summarize_session_notes(transcribed_text)
                        if summary:
                            session.summary = summary
                            session.save()
                    
                    success_message = "Audio wurde hochgeladen und transkribiert."
                    
                except Exception as e:
                    logger.error(f"Fehler bei der Transkription: {str(e)}")
                    success_message = f"Audio wurde hochgeladen, aber Transkription fehlgeschlagen: {str(e)}"
                    
                    if request.headers.get("HX-Request"):
                        return JsonResponse({"error": success_message}, status=400)
                    else:
                        messages.error(request, success_message)
                        return redirect(
                            "sessions:session_detail",
                            pk=session.pk,
                        )
            else:
                success_message = "Audio wurde hochgeladen."
            
            if request.headers.get("HX-Request"):
                return JsonResponse({"success": True, "message": success_message})
            else:
                messages.success(request, success_message)
                
        except Exception as e:
            logger.error(f"Fehler beim Hochladen: {str(e)}")
            error_message = f"Fehler beim Hochladen: {str(e)}"
            
            if request.headers.get("HX-Request"):
                return JsonResponse({"error": error_message}, status=400)
            else:
                messages.error(request, error_message)
        
        return redirect(
            "sessions:session_detail",
            pk=session.pk,
        )
    
    @action(detail=True, methods=['post'])
    def transcribe(self, request, pk=None):
        """Manually transcribe an audio recording"""
        recording = get_object_or_404(AudioRecording, pk=pk)
        
        transcription_service = get_transcription_service()
        if not transcription_service.is_available():
            messages.error(request, 'OpenAI API Key ist nicht konfiguriert.')
            session = recording.session
            return redirect("sessions:session_detail", pk=session.pk)
        
        try:
            # Check if already transcribed
            if hasattr(recording, 'transcription'):
                messages.info(request, 'Audio ist bereits transkribiert.')
                # Need to get the session to redirect properly
                session = recording.session
                return redirect("sessions:session_detail", pk=session.pk)
            
            # Transcribe audio
            file_path = recording.audio.path
            transcribed_text, processing_time = transcription_service.transcribe(file_path)
            
            # Create transcription
            Transcription.objects.create(
                recording=recording,
                text=transcribed_text,
                processing_time_seconds=processing_time
            )
            
            recording.is_processed = True
            recording.save()
            
            messages.success(request, 'Audio wurde erfolgreich transkribiert.')
            
        except Exception as e:
            logger.error(f'Fehler bei der Transkription: {str(e)}')
            messages.error(request, f'Fehler bei der Transkription: {str(e)}')
        
        # Need to get the session to redirect properly
        session = recording.session
        return redirect("sessions:session_detail", pk=session.pk)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download an audio recording"""
        recording = get_object_or_404(AudioRecording, pk=pk)
        
        if not recording.audio or not os.path.exists(recording.audio.path):
            raise Http404("Audio-Datei nicht gefunden")
        
        response = HttpResponse(
            open(recording.audio.path, 'rb').read(),
            content_type='audio/mpeg'
        )
        response['Content-Disposition'] = f'attachment; filename="{recording.filename}"'
        return response
    
    @action(detail=True, methods=['post'])
    @method_decorator(csrf_exempt)
    def delete(self, request, pk=None):
        """Delete an audio recording"""
        recording = get_object_or_404(AudioRecording, pk=pk)
        
        try:
            # Delete the audio file from disk
            if recording.audio and os.path.exists(recording.audio.path):
                os.remove(recording.audio.path)
            
            # Delete the recording (this will cascade to transcription)
            recording.delete()
            
            return JsonResponse({"success": True})
            
        except Exception as e:
            logger.error(f"Fehler beim Löschen: {str(e)}")
            return JsonResponse({"error": f"Fehler beim Löschen: {str(e)}"}, status=400) 