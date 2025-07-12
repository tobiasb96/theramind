from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets
from rest_framework.decorators import action
import json
import re
import logging
from django.core.paginator import Paginator
from django.shortcuts import render
from therapy.models import Session, Therapy, Transcription
from therapy.forms import SessionForm, AudioUploadForm
from transcriptions.services import get_transcription_service
from transcriptions.prompts import get_available_templates

logger = logging.getLogger(__name__)


class SessionViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing session CRUD operations and custom actions.
    """
    
    def get_queryset(self):
        return Session.objects.select_related('therapy__patient').order_by('-date')
    
    def get_object(self, patient_pk=None, therapy_pk=None, session_pk=None):
        """Get session with nested relationship validation"""
        if patient_pk and therapy_pk and session_pk:
            return get_object_or_404(
                Session, 
                pk=session_pk, 
                therapy__pk=therapy_pk, 
                therapy__patient__pk=patient_pk
            )
        elif session_pk:
            return get_object_or_404(Session, pk=session_pk)
        return None
    
    def list(self, request):
        """List all sessions"""
        sessions = self.get_queryset()
        
        paginator = Paginator(sessions, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'therapy/session_list.html', {
            'sessions': page_obj,
            'page_obj': page_obj,
        })
    
    def retrieve(self, request, patient_pk=None, therapy_pk=None, session_pk=None):
        """Retrieve a specific session"""
        session = self.get_object(patient_pk, therapy_pk, session_pk)
        
        # Get related data
        recordings = session.audiorecording_set.order_by('-created_at')
        upload_form = AudioUploadForm()
        session_notes_templates = get_available_templates()
        
        return render(request, 'therapy/session_detail.html', {
            'session': session,
            'recordings': recordings,
            'upload_form': upload_form,
            'session_notes_templates': session_notes_templates,
            'patient': session.therapy.patient,
            'therapy': session.therapy,
        })
    
    def create(self, request, patient_pk=None, therapy_pk=None):
        """Create a new session"""
        if request.method == 'GET':
            form = SessionForm()
            
            # Pre-populate therapy if provided
            if therapy_pk:
                try:
                    therapy = Therapy.objects.get(pk=therapy_pk, patient__pk=patient_pk)
                    form.initial['therapy'] = therapy
                except Therapy.DoesNotExist:
                    pass
            
            return render(request, 'therapy/session_form.html', {'form': form})
        
        elif request.method == 'POST':
            # Handle HTMX requests for session creation from patient detail page
            if request.headers.get("HX-Request"):
                return self._handle_htmx_create(request, patient_pk)
            
            form = SessionForm(request.POST)
            if form.is_valid():
                session = form.save(commit=False)
                
                # Set therapy from URL parameters or find/create one
                if therapy_pk:
                    therapy = get_object_or_404(Therapy, pk=therapy_pk, patient__pk=patient_pk)
                else:
                    # Find or create active therapy
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
                
                session.therapy = therapy
                session.save()
                
                messages.success(request, 'Sitzung wurde erfolgreich angelegt.')
                return HttpResponseRedirect(reverse_lazy(
                    "therapy:session_detail",
                    kwargs={
                        "patient_pk": patient_pk,
                        "therapy_pk": therapy.pk,
                        "session_pk": session.pk,
                    },
                ))
            
            return render(request, 'therapy/session_form.html', {'form': form})
    
    def _handle_htmx_create(self, request, patient_pk):
        """Handle HTMX session creation from patient detail page"""
        try:
            from patients.models import Patient
            patient = Patient.objects.get(pk=patient_pk)
            
            # Find or create an active therapy for this patient
            therapy = Therapy.objects.filter(patient=patient, status="active").first()
            if not therapy:
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
            response = HttpResponse()
            response["HX-Redirect"] = f"/patients/{patient_pk}/"
            return response
            
        except (Patient.DoesNotExist, ValueError):
            return JsonResponse({"error": "Fehler beim Erstellen der Sitzung"}, status=400)
    
    def update(self, request, patient_pk=None, therapy_pk=None, session_pk=None):
        """Update an existing session"""
        session = self.get_object(patient_pk, therapy_pk, session_pk)
        
        if request.method == 'GET':
            form = SessionForm(instance=session)
            return render(request, 'therapy/session_form.html', {'form': form, 'session': session})
        
        elif request.method == 'POST':
            # Handle HTMX requests
            if request.headers.get("HX-Request"):
                return self._handle_htmx_update(request, session, patient_pk, therapy_pk)
            
            form = SessionForm(request.POST, instance=session)
            if form.is_valid():
                # Handle session notes update if provided
                session_notes = request.POST.get("session_notes")
                if session_notes is not None:
                    session.notes = self._sanitize_html(session_notes)
                
                form.save()
                messages.success(request, 'Sitzung wurde erfolgreich aktualisiert.')
                return HttpResponseRedirect(reverse_lazy(
                    "therapy:session_detail",
                    kwargs={
                        "patient_pk": patient_pk,
                        "therapy_pk": therapy_pk,
                        "session_pk": session.pk,
                    },
                ))
            
            return render(request, 'therapy/session_form.html', {'form': form, 'session': session})
    
    def _handle_htmx_update(self, request, session, patient_pk, therapy_pk):
        """Handle HTMX session update"""
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, "Sitzung wurde erfolgreich aktualisiert.")
            
            response = HttpResponse("")
            response["HX-Redirect"] = reverse_lazy(
                "therapy:session_detail",
                kwargs={
                    "patient_pk": patient_pk,
                    "therapy_pk": therapy_pk,
                    "session_pk": session.pk,
                },
            )
            return response
        
        return JsonResponse({"error": "Fehler beim Aktualisieren"}, status=400)
    
    def destroy(self, request, patient_pk=None, therapy_pk=None, session_pk=None):
        """Delete a session"""
        session = self.get_object(patient_pk, therapy_pk, session_pk)
        
        if request.method == 'GET':
            return render(request, 'therapy/session_confirm_delete.html', {'session': session})
        
        elif request.method == 'POST':
            # Handle HTMX requests
            if request.headers.get("HX-Request"):
                success_url = reverse_lazy("patients:patient_detail", kwargs={"pk": patient_pk})
                session.delete()
                messages.success(request, "Sitzung wurde erfolgreich gelöscht.")
                
                response = HttpResponse()
                response["HX-Redirect"] = success_url
                return response
            
            session.delete()
            messages.success(request, "Sitzung wurde erfolgreich gelöscht.")
            return HttpResponseRedirect(reverse_lazy("patients:patient_detail", kwargs={"pk": patient_pk}))
    
    @action(detail=True, methods=['post'])
    @method_decorator(csrf_exempt)
    def save_transcript(self, request, patient_pk=None, therapy_pk=None, session_pk=None):
        """Save transcript text to session notes"""
        session = self.get_object(patient_pk, therapy_pk, session_pk)
        
        try:
            data = json.loads(request.body)
            transcript_text = data.get("transcript", "")
            
            # Save transcript as session notes
            session.notes = transcript_text
            session.save()
            
            return JsonResponse({"success": True})
        
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({"error": "Invalid data"}, status=400)
    
    @action(detail=True, methods=['post'])
    @method_decorator(csrf_exempt)
    def generate_notes(self, request, patient_pk=None, therapy_pk=None, session_pk=None):
        """Generate AI session notes from transcriptions"""
        session = self.get_object(patient_pk, therapy_pk, session_pk)
        
        try:
            template_key = request.POST.get("template")
            
            if not template_key:
                messages.error(request, "Template ist erforderlich")
                return self._redirect_to_session_detail(patient_pk, therapy_pk, session_pk)
            
            # Get all transcriptions for this session
            transcriptions = Transcription.objects.filter(recording__session=session)
            
            if not transcriptions.exists():
                messages.error(request, "Keine Transkriptionen für diese Sitzung verfügbar")
                return self._redirect_to_session_detail(patient_pk, therapy_pk, session_pk)
            
            # Combine all transcriptions
            combined_transcript = "\n\n".join([t.text for t in transcriptions])
            
            # Generate session notes
            transcription_service = get_transcription_service()
            if not transcription_service.is_available():
                messages.error(request, "OpenAI API Key ist nicht konfiguriert")
                return self._redirect_to_session_detail(patient_pk, therapy_pk, session_pk)
            
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
        
        return self._redirect_to_session_detail(patient_pk, therapy_pk, session_pk)
    
    @action(detail=True, methods=['post'])
    @method_decorator(csrf_exempt)
    def save_notes(self, request, patient_pk=None, therapy_pk=None, session_pk=None):
        """Save session notes with HTML sanitization"""
        session = self.get_object(patient_pk, therapy_pk, session_pk)
        
        try:
            session_notes = request.POST.get("session_notes", "")
            session.notes = self._sanitize_html(session_notes)
            session.save()
            
            messages.success(request, "Notizen wurden erfolgreich gespeichert.")
            
        except Exception as e:
            messages.error(request, f"Fehler beim Speichern: {str(e)}")
        
        return self._redirect_to_session_detail(patient_pk, therapy_pk, session_pk)
    
    def _sanitize_html(self, html_content):
        """Sanitize HTML content to allow only safe tags"""
        allowed_tags = ["p", "br", "strong", "b", "em", "i", "u", "ul", "ol", "li"]
        
        # Remove all tags except allowed ones
        pattern = re.compile(
            r"<(?!\/?(?:" + "|".join(allowed_tags) + r")\b)[^>]+>", re.IGNORECASE
        )
        html_content = pattern.sub("", html_content)
        
        # Remove all attributes for all tags
        for tag in allowed_tags:
            html_content = re.sub(r"<" + tag + r"[^>]*>", f"<{tag}>", html_content)
        
        return html_content
    
    def _redirect_to_session_detail(self, patient_pk, therapy_pk, session_pk):
        """Helper method to redirect to session detail"""
        return HttpResponseRedirect(reverse_lazy(
            "therapy:session_detail",
            kwargs={
                "patient_pk": patient_pk,
                "therapy_pk": therapy_pk,
                "session_pk": session_pk,
            },
        )) 