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
from sessions.models import Session, Transcription
from sessions.forms import SessionForm, AudioUploadForm
from sessions.services import get_transcription_service
from sessions.prompts import get_available_templates

logger = logging.getLogger(__name__)


class SessionViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing session CRUD operations and custom actions.
    """
    
    def get_queryset(self):
        return Session.objects.order_by("-date")

    def get_object(self, session_pk=None):
        """Get session with nested relationship validation"""
        if session_pk:
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

    def retrieve(self, request, session_pk=None):
        """Retrieve a specific session"""
        session = self.get_object(session_pk)

        # Get related data
        recordings = session.audiorecording_set.order_by("-created_at")
        upload_form = AudioUploadForm()
        session_notes_templates = get_available_templates()

        return render(
            request,
            "therapy/session_detail.html",
            {
                "session": session,
                "recordings": recordings,
                "upload_form": upload_form,
                "session_notes_templates": session_notes_templates,
            },
        )

    def create(self, request):
        """Create a new session"""
        if request.method == 'GET':
            form = SessionForm()

            return render(request, "therapy/session_form.html", {"form": form})

        elif request.method == "POST":
            form = SessionForm(request.POST)
            if form.is_valid():
                session = form.save(commit=False)
                messages.success(request, "Sitzung wurde erfolgreich angelegt.")
                return HttpResponseRedirect(
                    reverse_lazy("therapy:session_detail", kwargs={"session_pk": session.pk})
                )
            return render(request, "therapy/session_form.html", {"form": form})

    def _handle_htmx_create(self, request):
        """Handle HTMX session creation"""
        try:
            session = Session.objects.create(
                date=request.POST.get("date"),
                duration=int(request.POST.get("duration", 50)),
                title=request.POST.get("title", ""),
            )
            response = HttpResponse()
            response["HX-Redirect"] = reverse_lazy(
                "therapy:session_detail", kwargs={"session_pk": session.pk}
            )
            return response

        except ValueError:
            return JsonResponse({"error": "Fehler beim Erstellen der Sitzung"}, status=400)

    def update(self, request, session_pk=None):
        """Update an existing session"""
        session = self.get_object(session_pk)

        if request.method == "GET":
            form = SessionForm(instance=session)
            return render(request, "therapy/session_form.html", {"form": form, "session": session})

        elif request.method == "POST":
            form = SessionForm(request.POST, instance=session)
            if form.is_valid():
                session_notes = request.POST.get("session_notes")
                if session_notes is not None:
                    session.notes = self._sanitize_html(session_notes)

                form.save()
                messages.success(request, "Sitzung wurde erfolgreich aktualisiert.")
                return HttpResponseRedirect(
                    reverse_lazy(
                        "therapy:session_detail",
                        kwargs={"session_pk": session.pk},
                    )
                )

            return render(request, "therapy/session_form.html", {"form": form, "session": session})

    def _handle_htmx_update(self, request, session):
        """Handle HTMX session update"""
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
        messages.success(request, "Sitzung wurde erfolgreich aktualisiert.")

        response = HttpResponse("")
        response["HX-Redirect"] = reverse_lazy(
            "therapy:session_detail",
            kwargs={"session_pk": session.pk},
        )
        return response

    def destroy(self, request, session_pk=None):
        """Delete a session"""
        session = self.get_object(session_pk)

        if request.method == "GET":
            return render(request, "therapy/session_confirm_delete.html", {"session": session})

        elif request.method == "POST":
            session.delete()
            messages.success(request, "Sitzung wurde erfolgreich gelöscht.")

        return HttpResponseRedirect(reverse_lazy("therapy:session_list"))

    @action(detail=True, methods=["post"])
    @method_decorator(csrf_exempt)
    def save_transcript(self, request, session_pk=None):
        """Save transcript text to session notes"""
        session = self.get_object(session_pk)

        try:
            data = json.loads(request.body)
            transcript_text = data.get("transcript", "")
            session.notes = transcript_text
            session.save()

            return JsonResponse({"success": True})

        except (json.JSONDecodeError, KeyError):
            return JsonResponse({"error": "Invalid data"}, status=400)

    @action(detail=True, methods=["post"])
    @method_decorator(csrf_exempt)
    def generate_notes(self, request, session_pk=None):
        """Generate AI session notes from transcriptions"""
        session = self.get_object(session_pk)

        try:
            template_key = request.POST.get("template")

            if not template_key:
                messages.error(request, "Template ist erforderlich")
                return self._redirect_to_session_detail(session_pk)

            # Get all transcriptions for this session
            transcriptions = Transcription.objects.filter(recording__session=session)

            if not transcriptions.exists():
                messages.error(request, "Keine Transkriptionen für diese Sitzung verfügbar")
                return self._redirect_to_session_detail(session_pk)

            # Combine all transcriptions
            combined_transcript = "\n\n".join([t.text for t in transcriptions])

            # Generate session notes
            transcription_service = get_transcription_service()
            if not transcription_service.is_available():
                messages.error(request, "OpenAI API Key ist nicht konfiguriert")
                return self._redirect_to_session_detail(session_pk)

            # Pass existing notes to the AI service
            existing_notes = session.notes if session.notes else None

            session_notes = transcription_service.create_session_notes(
                combined_transcript, template_key, existing_notes
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

        return self._redirect_to_session_detail(session_pk)
    
    @action(detail=True, methods=['post'])
    @method_decorator(csrf_exempt)
    def save_notes(self, request, session_pk=None):
        """Save session notes with HTML sanitization"""
        session = self.get_object(session_pk)
        
        try:
            session_notes = request.POST.get("session_notes", "")
            session.notes = self._sanitize_html(session_notes)
            session.save()
            
            messages.success(request, "Notizen wurden erfolgreich gespeichert.")
            
        except Exception as e:
            messages.error(request, f"Fehler beim Speichern: {str(e)}")

        return self._redirect_to_session_detail(session_pk)

    @action(detail=True, methods=["post"])
    @method_decorator(csrf_exempt)
    def create_from_template(self, request, session_pk=None):
        """Create session notes from a template without audio transcriptions"""
        session = self.get_object(session_pk)

        try:
            template_key = request.POST.get("template")

            if not template_key:
                messages.error(request, "Template ist erforderlich")
                return self._redirect_to_session_detail(session_pk)

            # Get the template structure from prompts
            from sessions.prompts import SESSION_NOTES_TEMPLATES

            if template_key not in SESSION_NOTES_TEMPLATES:
                messages.error(request, "Unbekanntes Template")
                return self._redirect_to_session_detail(session_pk)

            template_data = SESSION_NOTES_TEMPLATES[template_key]

            # Extract the structure from the template prompt
            # Look for the structured part after "Strukturiere die Notizen wie folgt:"
            prompt = template_data["prompt"]
            structure_start = prompt.find("Strukturiere die Notizen wie folgt:")

            if structure_start != -1:
                # Find the end of the structure (before "Transkript der Sitzung:")
                structure_end = prompt.find("Transkript der Sitzung:")
                if structure_end != -1:
                    structure_html = prompt[
                        structure_start + len("Strukturiere die Notizen wie folgt:") : structure_end
                    ].strip()

                    # Clean up the structure to remove extra instructions
                    lines = structure_html.split("\n")
                    cleaned_lines = []
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith("Antworte in HTML-Format"):
                            cleaned_lines.append(line)

                    structure_html = "\n".join(cleaned_lines)

                    # Save the template structure as session notes
                    session.notes = structure_html
                    session.save()

                    messages.success(
                        request, f"Vorlage '{template_data['name']}' wurde erfolgreich angewendet."
                    )
                else:
                    messages.error(request, "Fehler beim Extrahieren der Template-Struktur")
            else:
                messages.error(request, "Fehler beim Verarbeiten des Templates")

        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Notizen aus Template: {str(e)}")
            messages.error(request, f"Fehler beim Erstellen der Notizen: {str(e)}")

        return self._redirect_to_session_detail(session_pk)

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

    def _redirect_to_session_detail(self, session_pk):
        """Helper method to redirect to session detail"""
        return HttpResponseRedirect(
            reverse_lazy(
                "therapy:session_detail",
                kwargs={"session_pk": session_pk},
            )
        )
