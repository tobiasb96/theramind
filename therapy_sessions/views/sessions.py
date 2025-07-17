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
from therapy_sessions.models import Session, Transcription
from therapy_sessions.forms import SessionForm, AudioUploadForm
from therapy_sessions.services import get_transcription_service

logger = logging.getLogger(__name__)


class SessionViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing session CRUD operations and custom actions.
    """
    
    def get_queryset(self):
        return Session.objects.order_by("-date")

    def get_object(self, pk=None):
        """Get session with nested relationship validation"""
        if pk:
            return get_object_or_404(Session, pk=pk)
        return None
    
    def list(self, request):
        """List all sessions"""
        sessions = self.get_queryset()
        
        paginator = Paginator(sessions, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(
            request,
            "sessions/session_list.html",
            {
                "sessions": page_obj,
                "page_obj": page_obj,
            },
        )

    def retrieve(self, request, pk=None):
        """Retrieve a specific session"""
        session = self.get_object(pk)

        # Get related data
        recordings = session.audiorecording_set.order_by("-created_at")
        upload_form = AudioUploadForm()

        # Get session notes templates from TemplateService
        from document_templates.service import TemplateService

        template_service = TemplateService()
        session_notes_templates = template_service.get_session_templates()

        return render(
            request,
            "sessions/session_detail.html",
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

            return render(request, "sessions/session_form.html", {"form": form})

        elif request.method == "POST":
            form = SessionForm(request.POST)
            if form.is_valid():
                session = form.save(commit=False)
                messages.success(request, "Sitzung wurde erfolgreich angelegt.")
                return HttpResponseRedirect(
                    reverse_lazy("sessions:session_detail", kwargs={"pk": session.pk})
                )
            return render(request, "sessions/session_form.html", {"form": form})

    def _handle_htmx_create(self, request):
        """Handle HTMX session creation"""
        try:
            session = Session.objects.create(
                date=request.POST.get("date"),
                title=request.POST.get("title", ""),
            )
            response = HttpResponse()
            response["HX-Redirect"] = reverse_lazy(
                "sessions:session_detail", kwargs={"pk": session.pk}
            )
            return response

        except ValueError:
            return JsonResponse({"error": "Fehler beim Erstellen der Sitzung"}, status=400)

    def update(self, request, pk=None):
        """Update an existing session"""
        session = self.get_object(pk)

        if request.method == "GET":
            form = SessionForm(instance=session)
            return render(request, "sessions/session_form.html", {"form": form, "session": session})

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
                        "sessions:session_detail",
                        kwargs={"pk": session.pk},
                    )
                )

            return render(request, "sessions/session_form.html", {"form": form, "session": session})

    def _handle_htmx_update(self, request, session):
        """Handle HTMX session update"""
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
        messages.success(request, "Sitzung wurde erfolgreich aktualisiert.")

        response = HttpResponse("")
        response["HX-Redirect"] = reverse_lazy(
            "sessions:session_detail",
            kwargs={"pk": session.pk},
        )
        return response

    def destroy(self, request, pk=None):
        """Delete a session"""
        session = self.get_object(pk)

        if request.method == "GET":
            return render(request, "sessions/session_confirm_delete.html", {"session": session})

        elif request.method == "POST":
            session.delete()
            messages.success(request, "Sitzung wurde erfolgreich gelöscht.")

        return HttpResponseRedirect(reverse_lazy("sessions:session_list"))

    @action(detail=True, methods=["post"])
    @method_decorator(csrf_exempt)
    def save_transcript(self, request, pk=None):
        """Save transcript text to session notes"""
        session = self.get_object(pk)

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
    def generate_notes(self, request, pk=None):
        """Generate AI session notes from transcriptions"""
        session = self.get_object(pk)

        try:
            template_id = request.POST.get("template")

            if not template_id:
                messages.error(request, "Template ist erforderlich")
                return self._redirect_to_session_detail(pk)

            # Get the template
            from document_templates.models import DocumentTemplate

            try:
                template = DocumentTemplate.objects.get(
                    id=template_id, template_type=DocumentTemplate.TemplateType.SESSION_NOTES
                )
            except DocumentTemplate.DoesNotExist:
                messages.error(request, "Template nicht gefunden")
                return self._redirect_to_session_detail(pk)

            # Get all transcriptions for this session
            transcriptions = Transcription.objects.filter(recording__session=session)

            if not transcriptions.exists():
                messages.error(request, "Keine Transkriptionen für diese Sitzung verfügbar")
                return self._redirect_to_session_detail(pk)

            # Combine all transcriptions
            combined_transcript = "\n\n".join([t.text for t in transcriptions])

            # Generate session notes
            transcription_service = get_transcription_service()
            if not transcription_service.is_available():
                messages.error(request, "OpenAI API Key ist nicht konfiguriert")
                return self._redirect_to_session_detail(pk)

            # Pass existing notes to the AI service
            existing_notes = session.notes if session.notes else None

            session_notes = transcription_service.create_session_notes_with_template(
                combined_transcript, template, existing_notes
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

        return self._redirect_to_session_detail(pk)
    
    @action(detail=True, methods=['post'])
    @method_decorator(csrf_exempt)
    def save_notes(self, request, pk=None):
        """Save session notes with HTML sanitization"""
        session = self.get_object(pk)
        
        try:
            session_notes = request.POST.get("session_notes", "")
            session.notes = self._sanitize_html(session_notes)
            session.save()

            # Return different responses based on request type
            if request.headers.get("HX-Request"):
                return HttpResponse("")  # Empty response for HTMX auto-save
            else:
                messages.success(request, "Notizen wurden erfolgreich gespeichert.")
                return self._redirect_to_session_detail(pk)

        except Exception as e:
            if request.headers.get("HX-Request"):
                return HttpResponse("", status=500)  # Error response for HTMX
            else:
                messages.error(request, f"Fehler beim Speichern: {str(e)}")
                return self._redirect_to_session_detail(pk)

    @action(detail=True, methods=["post"])
    @method_decorator(csrf_exempt)
    def create_from_template(self, request, pk=None):
        """Create session notes from a template without audio transcriptions"""
        session = self.get_object(pk)

        try:
            template_id = request.POST.get("template")

            if not template_id:
                messages.error(request, "Template ist erforderlich")
                return self._redirect_to_session_detail(pk)

            # Get the template
            from document_templates.models import DocumentTemplate

            try:
                template = DocumentTemplate.objects.get(
                    id=template_id, template_type=DocumentTemplate.TemplateType.SESSION_NOTES
                )
            except DocumentTemplate.DoesNotExist:
                messages.error(request, "Template nicht gefunden")
                return self._redirect_to_session_detail(pk)

            # Use the template's user_prompt as the structure for session notes
            # This is the template structure that will be filled out manually
            session.notes = template.user_prompt
            session.save()

            messages.success(request, f"Vorlage '{template.name}' wurde erfolgreich angewendet.")

        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Notizen aus Template: {str(e)}")
            messages.error(request, f"Fehler beim Erstellen der Notizen: {str(e)}")

        return self._redirect_to_session_detail(pk)

    @action(detail=True, methods=["post"])
    @method_decorator(csrf_exempt)
    def export_notes_pdf(self, request, pk=None):
        """Export session notes to PDF"""
        session = self.get_object(pk)

        try:
            # Use the export service with database content
            from core.services import PDFExportService

            export_service = PDFExportService()

            # Prepare title
            title = "Sitzungsnotizen"
            if session.title:
                title += f" - {session.title}"

            pdf_data = export_service.export_notes_to_pdf(
                title=title,
                date=session.date,
                content=session.notes,
                filename_prefix="Sitzungsnotizen",
            )

            # Create Django response
            response = HttpResponse(pdf_data["content"], content_type=pdf_data["content_type"])
            response["Content-Disposition"] = f"attachment; filename={pdf_data['filename']}"

            return response

        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            logger.error(f"Fehler beim Exportieren der Notizen als PDF: {str(e)}")
            return JsonResponse(
                {"error": f"Fehler beim Exportieren der Notizen als PDF: {str(e)}"}, status=500
            )

    @action(detail=True, methods=["post"])
    @method_decorator(csrf_exempt)
    def delete_notes(self, request, pk=None):
        """Delete session notes"""
        session = self.get_object(pk)

        try:
            session.notes = ""
            session.save()
            return JsonResponse(
                {"success": True, "message": "Sitzungsnotizen wurden erfolgreich gelöscht."}
            )
        except Exception as e:
            logger.error(f"Fehler beim Löschen der Notizen: {str(e)}")
            return JsonResponse({"error": f"Fehler beim Löschen der Notizen: {str(e)}"}, status=500)

    def _sanitize_html(self, html_content):
        """Sanitize HTML content to allow only safe tags"""

        allowed_tags = ["p", "br", "strong", "b", "em", "i", "u", "ul", "ol", "li"]

        # First, remove all attributes from allowed tags (but keep the tags themselves)
        for tag in allowed_tags:
            # Handle opening tags with attributes
            html_content = re.sub(
                r"<(" + re.escape(tag) + r")\s[^>]*>", r"<\1>", html_content, flags=re.IGNORECASE
            )

        # Remove all disallowed tags completely (opening and closing)
        # This pattern matches any tag that's not in our allowed list
        allowed_pattern = "|".join(re.escape(tag) for tag in allowed_tags)
        disallowed_pattern = re.compile(
            r"<(?!/?\s*(?:" + allowed_pattern + r")\s*(?:\s[^>]*)?/?)\s*[^>]*>", re.IGNORECASE
        )
        html_content = disallowed_pattern.sub("", html_content)

        # Clean up any malformed or empty tags
        html_content = re.sub(r"<\s*>", "", html_content)  # Remove empty tags like <>
        html_content = re.sub(r"<\s*/\s*>", "", html_content)  # Remove empty closing tags like </>

        return html_content

    def _redirect_to_session_detail(self, pk):
        """Helper method to redirect to session detail"""
        return HttpResponseRedirect(
            reverse_lazy(
                "sessions:session_detail",
                kwargs={"pk": pk},
            )
        )
