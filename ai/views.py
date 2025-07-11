from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.http import JsonResponse
from .services import get_ai_service
from therapy.models import Session, AudioRecording, Transcription


class TestAIView(TemplateView):
    template_name = 'ai/test.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ai_service = get_ai_service()
        context['ai_available'] = ai_service.is_available()
        return context
    
    def post(self, request, *args, **kwargs):
        """Test AI service availability via AJAX"""
        ai_service = get_ai_service()
        return JsonResponse({
            'available': ai_service.is_available(),
            'status': 'OpenAI service is available' if ai_service.is_available() else 'OpenAI service not available'
        })


class TranscribeAudioView(View):
    def post(self, request, recording_id):
        recording = get_object_or_404(AudioRecording, id=recording_id)
        
        ai_service = get_ai_service()
        if not ai_service.is_available():
            return JsonResponse({'error': 'OpenAI API Key ist nicht konfiguriert.'}, status=400)
        
        try:
            # Check if already transcribed
            if hasattr(recording, 'transcription'):
                return JsonResponse({'error': 'Audio ist bereits transkribiert.'}, status=400)
            
            # Transcribe audio
            file_path = recording.audio.path
            transcribed_text, processing_time = ai_service.transcribe(file_path)
            
            # Create transcription
            Transcription.objects.create(
                recording=recording, text=transcribed_text, processing_time_seconds=processing_time
            )
            
            recording.is_processed = True
            recording.save()
            
            return JsonResponse({
                'success': True,
                'text': transcribed_text,
                'processing_time': processing_time
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class SummarizeSessionView(View):
    def post(self, request, session_id):
        session = get_object_or_404(Session, id=session_id)
        
        ai_service = get_ai_service()
        if not ai_service.is_available():
            return JsonResponse({'error': 'OpenAI API Key ist nicht konfiguriert.'}, status=400)
        
        try:
            # Collect all transcriptions for this session
            transcriptions = []
            for recording in session.audiorecording_set.all():
                if hasattr(recording, 'transcription'):
                    transcriptions.append(recording.transcription.text)
            
            if not transcriptions:
                return JsonResponse({'error': 'Keine Transkriptionen für diese Sitzung gefunden.'}, status=400)
            
            # Combine all transcriptions
            combined_text = "\n\n".join(transcriptions)
            
            # Summarize
            summary = ai_service.summarize(combined_text)
            
            # Update session
            session.summary = summary
            session.save()
            
            return JsonResponse({
                'success': True,
                'summary': summary
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
