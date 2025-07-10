from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Session, AudioRecording, Transcription, Therapy, Document
from .forms import SessionForm, AudioUploadForm, TherapyForm, DocumentForm
from ai.services import get_ai_service
import json
import os


# Therapy Views
class TherapyListView(ListView):
    model = Therapy
    template_name = 'therapy/therapy_list.html'
    context_object_name = 'therapies'
    paginate_by = 20
    
    def get_queryset(self):
        return Therapy.objects.all().order_by('-start_date')


class TherapyDetailView(DetailView):
    model = Therapy
    template_name = 'therapy/therapy_detail.html'
    context_object_name = 'therapy'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = self.object.session_set.order_by('-date')
        context['documents'] = self.object.document_set.order_by('-created_at')
        return context


class TherapyCreateView(CreateView):
    model = Therapy
    form_class = TherapyForm
    template_name = 'therapy/therapy_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        patient_id = self.request.GET.get('patient')
        if patient_id:
            try:
                from core.models import Patient
                patient = Patient.objects.get(pk=patient_id)
                initial['patient'] = patient
            except Patient.DoesNotExist:
                pass
        return initial
    
    def get_success_url(self):
        return reverse_lazy('therapy:therapy_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Therapie wurde erfolgreich angelegt.')
        return super().form_valid(form)


class TherapyUpdateView(UpdateView):
    model = Therapy
    form_class = TherapyForm
    template_name = 'therapy/therapy_form.html'
    
    def get_success_url(self):
        return reverse_lazy('therapy:therapy_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Therapie wurde erfolgreich aktualisiert.')
        return super().form_valid(form)


class TherapyDeleteView(DeleteView):
    model = Therapy
    template_name = 'therapy/therapy_confirm_delete.html'
    success_url = reverse_lazy('therapy:therapy_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Therapie wurde erfolgreich gelöscht.')
        return super().form_valid(form)


# Session Views
class SessionListView(ListView):
    model = Session
    template_name = 'therapy/session_list.html'
    context_object_name = 'sessions'
    paginate_by = 20
    
    def get_queryset(self):
        return Session.objects.select_related('therapy__patient').order_by('-date')


class SessionDetailView(DetailView):
    model = Session
    template_name = 'therapy/session_detail.html'
    context_object_name = 'session'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recordings'] = self.object.audiorecording_set.order_by('-created_at')
        context['upload_form'] = AudioUploadForm()
        return context


class SessionCreateView(CreateView):
    model = Session
    form_class = SessionForm
    template_name = 'therapy/session_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        therapy_id = self.request.GET.get('therapy')
        if therapy_id:
            try:
                therapy = Therapy.objects.get(pk=therapy_id)
                initial['therapy'] = therapy
            except Therapy.DoesNotExist:
                pass
        return initial
    
    def get_success_url(self):
        return reverse_lazy('therapy:session_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Sitzung wurde erfolgreich angelegt.')
        return super().form_valid(form)


class SessionUpdateView(UpdateView):
    model = Session
    form_class = SessionForm
    template_name = 'therapy/session_form.html'
    
    def get_success_url(self):
        return reverse_lazy('therapy:session_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Sitzung wurde erfolgreich aktualisiert.')
        return super().form_valid(form)


class SessionDeleteView(DeleteView):
    model = Session
    template_name = 'therapy/session_confirm_delete.html'
    success_url = reverse_lazy('therapy:session_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Sitzung wurde erfolgreich gelöscht.')
        return super().form_valid(form)


# Document Views
class DocumentListView(ListView):
    model = Document
    template_name = 'therapy/document_list.html'
    context_object_name = 'documents'
    paginate_by = 20
    
    def get_queryset(self):
        return Document.objects.select_related('therapy__patient').order_by('-created_at')


class DocumentDetailView(DetailView):
    model = Document
    template_name = 'therapy/document_detail.html'
    context_object_name = 'document'


class DocumentCreateView(CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'therapy/document_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        therapy_id = self.request.GET.get('therapy')
        if therapy_id:
            try:
                therapy = Therapy.objects.get(pk=therapy_id)
                initial['therapy'] = therapy
            except Therapy.DoesNotExist:
                pass
        return initial
    
    def get_success_url(self):
        return reverse_lazy('therapy:document_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Dokument wurde erfolgreich angelegt.')
        return super().form_valid(form)


class DocumentUpdateView(UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'therapy/document_form.html'
    
    def get_success_url(self):
        return reverse_lazy('therapy:document_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Dokument wurde erfolgreich aktualisiert.')
        return super().form_valid(form)


class DocumentDeleteView(DeleteView):
    model = Document
    template_name = 'therapy/document_confirm_delete.html'
    success_url = reverse_lazy('therapy:document_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Dokument wurde erfolgreich gelöscht.')
        return super().form_valid(form)


@method_decorator(csrf_exempt, name='dispatch')
class AudioUploadView(View):
    def post(self, request, pk):
        session = get_object_or_404(Session, pk=pk)
        
        if 'audio' not in request.FILES:
            return JsonResponse({'error': 'Keine Audio-Datei hochgeladen'}, status=400)
        
        audio_file = request.FILES['audio']
        
        # Create audio recording
        recording = AudioRecording.objects.create(
            session=session,
            audio=audio_file,
            file_size=audio_file.size
        )
        
        # Auto-transcribe if enabled
        from core.models import Settings
        settings = Settings.get_settings()
        
        ai_service = get_ai_service()
        if settings.auto_transcribe and ai_service.is_available():
            try:
                # Transcribe audio
                file_path = recording.audio.path
                transcribed_text, processing_time = ai_service.transcribe(file_path)
                
                # Create transcription
                Transcription.objects.create(
                    recording=recording,
                    text=transcribed_text,
                    processing_time_seconds=processing_time
                )
                
                recording.is_processed = True
                recording.save()
                
                # Auto-summarize if enabled
                if settings.auto_summarize and transcribed_text:
                    summary = ai_service.summarize(transcribed_text)
                    if summary:
                        session.summary = summary
                        session.save()
                
                messages.success(request, 'Audio wurde hochgeladen und transkribiert.')
                
            except Exception as e:
                messages.error(request, f'Fehler bei der Transkription: {str(e)}')
        else:
            messages.success(request, 'Audio wurde hochgeladen.')
        
        return redirect('therapy:session_detail', pk=session.pk)


class TranscribeView(View):
    def post(self, request, pk):
        recording = get_object_or_404(AudioRecording, pk=pk)
        
        ai_service = get_ai_service()
        if not ai_service.is_available():
            messages.error(request, 'OpenAI API Key ist nicht konfiguriert.')
            return redirect('therapy:session_detail', pk=recording.session.pk)
        
        try:
            # Check if already transcribed
            if hasattr(recording, 'transcription'):
                messages.info(request, 'Audio ist bereits transkribiert.')
                return redirect('therapy:session_detail', pk=recording.session.pk)
            
            # Transcribe audio
            file_path = recording.audio.path
            transcribed_text, processing_time = ai_service.transcribe(file_path)
            
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
            messages.error(request, f'Fehler bei der Transkription: {str(e)}')
        
        return redirect('therapy:session_detail', pk=recording.session.pk)


class AudioDownloadView(View):
    def get(self, request, pk):
        recording = get_object_or_404(AudioRecording, pk=pk)
        
        if not recording.audio or not os.path.exists(recording.audio.path):
            raise Http404("Audio-Datei nicht gefunden")
        
        response = HttpResponse(
            open(recording.audio.path, 'rb').read(),
            content_type='audio/mpeg'
        )
        response['Content-Disposition'] = f'attachment; filename="{recording.filename}"'
        return response
