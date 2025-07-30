from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
import json
import re
import logging
from core.forms import AudioInputForm, DocumentFileInputForm, DocumentTextInputForm

from django.shortcuts import render
from core.services import PDFExportService
from therapy_sessions.models import Session
from therapy_sessions.forms import SessionForm
from therapy_sessions.services import get_session_service
from therapy_sessions.tasks import generate_session_notes_task
from document_templates.models import DocumentTemplate
from document_templates.service import TemplateService

logger = logging.getLogger(__name__)


class SessionViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing session CRUD operations and custom actions.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self, request=None):
        if request is None:
            raise ValueError("Request is required for get_queryset")
        return Session.objects.filter(user=request.user).order_by("-date")

    def get_object(self, pk=None, request=None):
        """Get session with nested relationship validation"""
        if pk:
            if request is None:
                raise ValueError("Request is required for get_object")
            return get_object_or_404(Session, pk=pk, user=request.user)
        return None

    def retrieve(self, request, pk=None):
        """Retrieve a specific session"""
        session = self.get_object(pk, request)

        # Get unified inputs
        audio_inputs = session.audio_inputs.order_by("-created_at")
        document_inputs = session.document_inputs.order_by("-created_at")
        audio_form = AudioInputForm()
        document_file_form = DocumentFileInputForm()
        document_text_form = DocumentTextInputForm()

        # Check if any audio input has a transcription
        has_transcribed_recordings = any(
            audio_input.transcribed_text for audio_input in audio_inputs
        )

        template_service = TemplateService()
        session_notes_templates = template_service.get_session_templates(user=request.user)

        # Get context summary
        session_service = get_session_service()
        context_summary = session_service.get_context_summary(session)

        # Check if session notes are being generated
        update_generation_status = session.is_generating

        # Check if any audio or document inputs are being processed
        any_inputs_processing = (
                audio_inputs.filter(processing_successful=None).exists()
                or document_inputs.filter(processing_successful=None).exists()
        )

        if request.headers.get("HX-Request") and bool(request.GET.get("update_generation_status", False)):
            return render(
                request,
                "partials/session_notes_card_with_session_summary.html",
                {
                    "session": session,
                    "session_notes": session.notes,
                    "update_generation_status": update_generation_status,
                },
            )

        if request.headers.get("HX-Request") and bool(request.GET.get("update_session_material", False)):
            return render(
                request,
                "partials/input_display_with_material_session_ready.html",
                {
                    "session": session,
                    "any_inputs_processing": any_inputs_processing,
                    "audio_inputs": audio_inputs,
                    "document_inputs": document_inputs,
                },
            )

        return render(
            request,
            "sessions/session_detail.html",
            {
                "session": session,
                "update_generation_status": update_generation_status,
                "any_inputs_processing": any_inputs_processing,
                "audio_inputs": audio_inputs,
                "document_inputs": document_inputs,
                "audio_form": audio_form,
                "document_file_form": document_file_form,
                "document_text_form": document_text_form,
                "session_notes_templates": session_notes_templates,
                "has_transcribed_recordings": has_transcribed_recordings,
                "context_summary": context_summary,
            },
        )

    def create(self, request):
        """Create a new session"""
        if request.method == "GET":
            form = SessionForm(user=request.user)

            # Check if this is a modal request (from dashboard)
            if request.headers.get("HX-Request") or request.GET.get("modal"):
                return render(request, "sessions/session_form_modal.html", {"form": form})

            return render(request, "sessions/session_form.html", {"form": form})

        elif request.method == "POST":
            form = SessionForm(request.POST, user=request.user)
            if form.is_valid():
                session = form.save()
                messages.success(request, "Sitzung wurde erfolgreich angelegt.")

                # Check if this is a modal/HTMX request
                if request.headers.get("HX-Request") or request.POST.get("modal"):
                    from django.http import HttpResponse

                    # Return JavaScript to close modal and redirect
                    response = HttpResponse()
                    response["HX-Trigger"] = "closeModal"
                    response["HX-Redirect"] = f"/sessions/{session.pk}/"
                    return response

                return HttpResponseRedirect(
                    reverse_lazy("sessions:session_detail", kwargs={"pk": session.pk})
                )

            # Check if this is a modal request for error handling
            if request.headers.get("HX-Request") or request.POST.get("modal"):
                return render(request, "sessions/session_form_modal.html", {"form": form})

            return render(request, "sessions/session_form.html", {"form": form})

    def update(self, request, pk=None):
        """Update an existing session"""
        session = self.get_object(pk, request)

        if request.method == "GET":
            form = SessionForm(instance=session, user=request.user)
            return render(request, "sessions/session_form.html", {"form": form, "session": session})

        elif request.method == "POST":
            form = SessionForm(request.POST, instance=session, user=request.user)
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

    def destroy(self, request, pk=None):
        """Delete a session"""
        session = self.get_object(pk, request)

        if request.method == "GET":
            return render(request, "sessions/session_confirm_delete.html", {"session": session})

        elif request.method == "POST":
            session.delete()
            messages.success(request, "Sitzung wurde erfolgreich gelöscht.")

        return HttpResponseRedirect(reverse_lazy("core:dashboard"))

    @action(detail=True, methods=["post"])
    @method_decorator(csrf_exempt)
    def save_transcript(self, request, pk=None):
        """Save transcript text to session notes"""
        session = self.get_object(pk, request)

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
        """Generate AI session notes from unified inputs in background task"""
        session = self.get_object(pk, request)

        try:
            template_id = request.POST.get("template")

            if not template_id:
                messages.error(request, "Template ist erforderlich")
                return self._redirect_to_session_detail(pk)

            session_service = get_session_service()
            context_summary = session_service.get_context_summary(session)
            if context_summary["total_inputs"] == 0:
                messages.error(request, "Keine Eingaben für diese Sitzung verfügbar")
                return self._redirect_to_session_detail(pk)

            if session.is_generating:
                messages.error(request, "Sitzungsnotizen werden bereits generiert")
                return self._redirect_to_session_detail(pk)

            existing_notes = session.notes if session.notes else None
            generate_session_notes_task.delay(
                session_id=session.id,
                template_id=int(template_id),
                user_id=request.user.id,
                existing_notes=existing_notes,
            )

            messages.success(
                request,
                "KI-Notizengenerierung wurde gestartet. Die Seite wird automatisch aktualisiert.",
            )

        except Exception as e:
            logger.error(f"Error starting session notes generation: {str(e)}")
            messages.error(request, f"Fehler beim Starten der Generierung: {str(e)}")

        return self._redirect_to_session_detail(pk)

    @action(detail=True, methods=["post"])
    def save_notes(self, request, pk=None):
        """Save session notes with HTML sanitization"""
        session = self.get_object(pk, request)

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
        session = self.get_object(pk, request)

        try:
            template_id = request.POST.get("template")

            if not template_id:
                messages.error(request, "Template ist erforderlich")
                return self._redirect_to_session_detail(pk)

            try:
                template = DocumentTemplate.objects.get_template(
                    int(template_id), DocumentTemplate.TemplateType.SESSION_NOTES, user=request.user
                )
            except Exception:
                messages.error(request, "Template nicht gefunden")
                return self._redirect_to_session_detail(pk)

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
        session = self.get_object(pk, request)

        try:
            export_service = PDFExportService()

            title = "Sitzungsnotizen"
            if session.title:
                title += f" - {session.title}"

            pdf_data = export_service.export_notes_to_pdf(
                title=title,
                date=session.date,
                content=session.notes,
                filename_prefix="Sitzungsnotizen",
            )

            session.mark_as_exported()
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
        session = self.get_object(pk, request)

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
