from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Session, AudioRecording, Transcription, Therapy
from .forms import SessionForm, AudioUploadForm, TherapyForm
from transcriptions.services import get_transcription_service
from transcriptions.prompts import get_available_templates
import json
import os
import logging

logger = logging.getLogger(__name__)


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
                from patients.models import Patient
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
    template_name = "therapy/session_detail.html"
    context_object_name = 'sessions'
    paginate_by = 20
    
    def get_queryset(self):
        return Session.objects.select_related('therapy__patient').order_by('-date')


class SessionDetailView(DetailView):
    model = Session
    template_name = 'therapy/session_detail.html'
    context_object_name = 'session'
    pk_url_kwarg = "session_pk"

    def get_object(self, queryset=None):
        patient_pk = self.kwargs.get("patient_pk")
        therapy_pk = self.kwargs.get("therapy_pk")
        session_pk = self.kwargs.get("session_pk")

        # Validate the nested relationship
        session = get_object_or_404(
            Session, pk=session_pk, therapy__pk=therapy_pk, therapy__patient__pk=patient_pk
        )
        return session
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recordings'] = self.object.audiorecording_set.order_by('-created_at')
        context['upload_form'] = AudioUploadForm()
        context["session_notes_templates"] = get_available_templates()

        # Add patient and therapy for breadcrumbs
        context["patient"] = self.object.therapy.patient
        context["therapy"] = self.object.therapy
        return context


class SessionCreateView(CreateView):
    model = Session
    form_class = SessionForm
    template_name = 'therapy/session_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        therapy_pk = self.kwargs.get("therapy_pk")
        if therapy_pk:
            try:
                therapy = Therapy.objects.get(pk=therapy_pk)
                initial['therapy'] = therapy
            except Therapy.DoesNotExist:
                pass
        return initial
    
    def get_success_url(self):
        return reverse_lazy(
            "therapy:session_detail",
            kwargs={
                "patient_pk": self.kwargs.get("patient_pk"),
                "therapy_pk": self.object.therapy.pk,
                "session_pk": self.object.pk,
            },
        )
    
    def form_valid(self, form):
        # Set the therapy from URL parameters or find/create one
        therapy_pk = self.kwargs.get("therapy_pk")
        patient_pk = self.kwargs.get("patient_pk")

        if therapy_pk:
            # Full nested URL - use specific therapy
            therapy = get_object_or_404(Therapy, pk=therapy_pk, patient__pk=patient_pk)
        else:
            # Simple URL - find or create active therapy
            from patients.models import Patient

            patient = get_object_or_404(Patient, pk=patient_pk)

            therapy = Therapy.objects.filter(patient=patient, status="active").first()
            if not therapy:
                therapy = Therapy.objects.create(
                    patient=patient,
                    title=f"Therapie für {patient.full_name}",
                    description="Automatisch erstellt",
                    status="active",
                )

        form.instance.therapy = therapy

        messages.success(self.request, 'Sitzung wurde erfolgreich angelegt.')
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        # Handle HTMX requests for session creation from patient detail page
        if request.headers.get("HX-Request"):
            patient_id = request.POST.get("patient")
            if patient_id:
                try:
                    from patients.models import Patient

                    patient = Patient.objects.get(pk=patient_id)

                    # Find or create an active therapy for this patient
                    therapy = Therapy.objects.filter(patient=patient, status="active").first()

                    if not therapy:
                        # Create a new therapy if none exists
                        therapy = Therapy.objects.create(
                            patient=patient,
                            title=f"Therapie für {patient.full_name}",
                            description="Automatisch erstellt",
                            status="active",
                        )

                    # Create the session
                    session = Session.objects.create(
                        therapy=therapy,
                        date=request.POST.get("date"),
                        duration=int(request.POST.get("duration", 50)),
                        title=request.POST.get("title", ""),
                    )

                    # Return success response for HTMX
                    from django.http import HttpResponse

                    response = HttpResponse()
                    response["HX-Redirect"] = f"/patients/{patient_id}/"
                    return response

                except (Patient.DoesNotExist, ValueError) as e:
                    from django.http import JsonResponse

                    return JsonResponse({"error": "Fehler beim Erstellen der Sitzung"}, status=400)

        # Fall back to regular form handling
        return super().post(request, *args, **kwargs)


class SessionUpdateView(UpdateView):
    model = Session
    form_class = SessionForm
    template_name = 'therapy/session_form.html'
    pk_url_kwarg = "session_pk"

    def get_object(self, queryset=None):
        patient_pk = self.kwargs.get("patient_pk")
        therapy_pk = self.kwargs.get("therapy_pk")
        session_pk = self.kwargs.get("session_pk")

        # Validate the nested relationship
        session = get_object_or_404(
            Session, pk=session_pk, therapy__pk=therapy_pk, therapy__patient__pk=patient_pk
        )
        return session
    
    def get_success_url(self):
        return reverse_lazy(
            "therapy:session_detail",
            kwargs={
                "patient_pk": self.kwargs.get("patient_pk"),
                "therapy_pk": self.kwargs.get("therapy_pk"),
                "session_pk": self.object.pk,
            },
        )
    
    def form_valid(self, form):
        # Handle HTMX requests
        if self.request.headers.get("HX-Request"):
            # Set the therapy (since it's not in the form)
            form.instance.therapy = self.object.therapy
            # Save the form
            self.object = form.save()
            messages.success(self.request, "Sitzung wurde erfolgreich aktualisiert.")
            from django.http import HttpResponse

            # Return empty response with redirect - HTMX will handle the redirect
            response = HttpResponse("")
            response["HX-Redirect"] = self.get_success_url()
            return response

        messages.success(self.request, 'Sitzung wurde erfolgreich aktualisiert.')
        return super().form_valid(form)


class SessionDeleteView(DeleteView):
    model = Session
    template_name = 'therapy/session_confirm_delete.html'
    pk_url_kwarg = "session_pk"

    def get_object(self, queryset=None):
        patient_pk = self.kwargs.get("patient_pk")
        therapy_pk = self.kwargs.get("therapy_pk")
        session_pk = self.kwargs.get("session_pk")

        # Validate the nested relationship
        session = get_object_or_404(
            Session, pk=session_pk, therapy__pk=therapy_pk, therapy__patient__pk=patient_pk
        )
        return session

    def get_success_url(self):
        return reverse_lazy("patients:patient_detail", kwargs={"pk": self.kwargs.get("patient_pk")})

    def post(self, request, *args, **kwargs):
        # Handle HTMX requests
        if request.headers.get("HX-Request"):
            self.object = self.get_object()
            success_url = self.get_success_url()
            self.object.delete()
            messages.success(request, "Sitzung wurde erfolgreich gelöscht.")
            from django.http import HttpResponse

            response = HttpResponse()
            response["HX-Redirect"] = success_url
            return response

        # Fall back to regular delete handling
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Sitzung wurde erfolgreich gelöscht.")
        return super().delete(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class AudioUploadView(View):
    def post(self, request, patient_pk, therapy_pk, session_pk):
        # Validate the nested relationship
        session = get_object_or_404(
            Session, pk=session_pk, therapy__pk=therapy_pk, therapy__patient__pk=patient_pk
        )
        if 'audio' not in request.FILES:
            if request.headers.get("HX-Request"):
                return JsonResponse({"error": "Keine Audio-Datei hochgeladen"}, status=400)
            else:
                messages.error(request, "Keine Audio-Datei hochgeladen")
                return redirect(
                    "therapy:session_detail",
                    patient_pk=patient_pk,
                    therapy_pk=therapy_pk,
                    session_pk=session_pk,
                )
        
        audio_file = request.FILES['audio']

        try:
            # Create audio recording
            recording = AudioRecording.objects.create(
                session=session, audio=audio_file, file_size=audio_file.size
            )

            # Auto-transcribe if enabled
            from patients.models import Settings

            settings = Settings.get_settings()

            transcription_service = get_transcription_service()
            if settings.auto_transcribe and transcription_service.is_available():
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
                    if settings.auto_summarize and transcribed_text:
                        summary = transcription_service.summarize(transcribed_text)
                        if summary:
                            session.summary = summary
                            session.save()

                    if request.headers.get("HX-Request"):
                        return JsonResponse(
                            {
                                "success": True,
                                "message": "Audio wurde hochgeladen und transkribiert.",
                            }
                        )
                    else:
                        messages.success(request, "Audio wurde hochgeladen und transkribiert.")

                except Exception as e:
                    if request.headers.get("HX-Request"):
                        return JsonResponse(
                            {"error": f"Fehler bei der Transkription: {str(e)}"}, status=400
                        )
                    else:
                        messages.error(request, f"Fehler bei der Transkription: {str(e)}")
            else:
                if request.headers.get("HX-Request"):
                    return JsonResponse({"success": True, "message": "Audio wurde hochgeladen."})
                else:
                    messages.success(request, "Audio wurde hochgeladen.")

        except Exception as e:
            if request.headers.get("HX-Request"):
                return JsonResponse({"error": f"Fehler beim Hochladen: {str(e)}"}, status=400)
            else:
                messages.error(request, f"Fehler beim Hochladen: {str(e)}")

        return redirect(
            "therapy:session_detail",
            patient_pk=patient_pk,
            therapy_pk=therapy_pk,
            session_pk=session_pk,
        )


class TranscribeView(View):
    def post(self, request, pk):
        recording = get_object_or_404(AudioRecording, pk=pk)

        transcription_service = get_transcription_service()
        if not transcription_service.is_available():
            messages.error(request, 'OpenAI API Key ist nicht konfiguriert.')
            return redirect('therapy:session_detail', pk=recording.session.pk)
        
        try:
            # Check if already transcribed
            if hasattr(recording, 'transcription'):
                messages.info(request, 'Audio ist bereits transkribiert.')
                return redirect('therapy:session_detail', pk=recording.session.pk)
            
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


@method_decorator(csrf_exempt, name="dispatch")
class AudioDeleteView(View):
    def post(self, request, pk):
        recording = get_object_or_404(AudioRecording, pk=pk)

        try:
            # Delete the audio file from disk
            if recording.audio and os.path.exists(recording.audio.path):
                os.remove(recording.audio.path)

            # Delete the recording (this will cascade to transcription)
            recording.delete()

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"error": f"Fehler beim Löschen: {str(e)}"}, status=400)


class SaveTranscriptView(View):
    def post(self, request, patient_pk, therapy_pk, session_pk):
        # Validate the nested relationship
        session = get_object_or_404(
            Session, pk=session_pk, therapy__pk=therapy_pk, therapy__patient__pk=patient_pk
        )

        try:
            data = json.loads(request.body)
            transcript_text = data.get("transcript", "")

            # Save transcript as session notes for now
            # In the future, we could create a separate Transcript model
            session.notes = transcript_text
            session.save()

            return JsonResponse({"success": True})

        except (json.JSONDecodeError, KeyError) as e:
            return JsonResponse({"error": "Invalid data"}, status=400)


@method_decorator(csrf_exempt, name="dispatch")
class GenerateSessionNotesView(View):
    def post(self, request, patient_pk, therapy_pk, session_pk):
        # Validate the nested relationship
        session = get_object_or_404(
            Session, pk=session_pk, therapy__pk=therapy_pk, therapy__patient__pk=patient_pk
        )

        try:
            template_key = request.POST.get("template")

            if not template_key:
                messages.error(request, "Template ist erforderlich")
                return redirect(
                    "therapy:session_detail",
                    patient_pk=patient_pk,
                    therapy_pk=therapy_pk,
                    session_pk=session_pk,
                )

            # Get all transcriptions for this session
            transcriptions = Transcription.objects.filter(recording__session=session)

            if not transcriptions.exists():
                messages.error(request, "Keine Transkriptionen für diese Sitzung verfügbar")
                return redirect(
                    "therapy:session_detail",
                    patient_pk=patient_pk,
                    therapy_pk=therapy_pk,
                    session_pk=session_pk,
                )

            # Combine all transcriptions
            combined_transcript = "\n\n".join([t.text for t in transcriptions])

            # Generate session notes
            transcription_service = get_transcription_service()
            if not transcription_service.is_available():
                messages.error(request, "OpenAI API Key ist nicht konfiguriert")
                return redirect(
                    "therapy:session_detail",
                    patient_pk=patient_pk,
                    therapy_pk=therapy_pk,
                    session_pk=session_pk,
                )

            session_notes = transcription_service.create_session_notes(
                combined_transcript, template_key
            )

            if session_notes:
                try:
                    summary = transcription_service.summarize_session_notes(session_notes)
                    session.summary = summary
                except Exception as e:
                    logger.error(f"Fehler bei der Zusammenfassung: {str(e)}")
                    pass

            session.notes = session_notes
            session.save()

            messages.success(request, "KI-Notizen wurden erfolgreich generiert!")

        except Exception as e:
            messages.error(request, f"Fehler bei der Generierung: {str(e)}")

        return redirect(
            "therapy:session_detail",
            patient_pk=patient_pk,
            therapy_pk=therapy_pk,
            session_pk=session_pk,
        )


@method_decorator(csrf_exempt, name="dispatch")
class SaveSessionNotesView(View):
    def post(self, request, patient_pk, therapy_pk, session_pk):
        # Validate the nested relationship
        session = get_object_or_404(
            Session, pk=session_pk, therapy__pk=therapy_pk, therapy__patient__pk=patient_pk
        )

        try:
            session_notes = request.POST.get("session_notes", "")

            # Basic HTML sanitization - allow only safe tags
            import re

            allowed_tags = [
                "p",
                "br",
                "strong",
                "b",
                "em",
                "i",
                "u",
                "ul",
                "ol",
                "li",
            ]

            # Remove all tags except allowed ones
            pattern = re.compile(
                r"<(?!\/?(?:" + "|".join(allowed_tags) + r")\b)[^>]+>", re.IGNORECASE
            )
            session_notes = pattern.sub("", session_notes)

            # Remove all attributes for all tags
            for tag in allowed_tags:
                session_notes = re.sub(r"<" + tag + r"[^>]*>", f"<{tag}>", session_notes)

            # Save session notes
            session.notes = session_notes
            session.save()

            messages.success(request, "Notizen wurden erfolgreich gespeichert.")

        except Exception as e:
            messages.error(request, f"Fehler beim Speichern: {str(e)}")

        return redirect(
            "therapy:session_detail",
            patient_pk=patient_pk,
            therapy_pk=therapy_pk,
            session_pk=session_pk,
        )
