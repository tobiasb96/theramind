from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
import json
import logging
from .tasks import generate_report_content_task

from document_templates.models import DocumentTemplate
from document_templates.service import TemplateService

from .models import Report
from .forms import ReportForm, ReportContentForm
from core.forms import AudioInputForm, DocumentFileInputForm, DocumentTextInputForm
from .services import ReportService

logger = logging.getLogger(__name__)


class ReportViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing report CRUD operations and custom actions.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self, request=None):
        if request is None:
            raise ValueError("Request is required for get_queryset")
        return Report.objects.filter(user=request.user).order_by("-created_at")

    def retrieve(self, request, pk=None):
        """Retrieve a specific report detail view"""
        # CRITICAL SECURITY: Only allow access to user's own reports
        report = get_object_or_404(Report, pk=pk, user=request.user)

        # Get unified inputs
        audio_inputs = report.audio_inputs.order_by("-created_at")
        document_inputs = report.document_inputs.order_by("-created_at")

        # Get available templates for report generation
        template_service = TemplateService()
        report_templates = template_service.get_available_templates(
            DocumentTemplate.TemplateType.REPORT, user=request.user
        )

        # Initialize unified forms
        audio_form = AudioInputForm()
        document_file_form = DocumentFileInputForm()
        document_text_form = DocumentTextInputForm()
        content_form = ReportContentForm(instance=report)
        
        # Get context summary
        report_service = ReportService()
        context_summary = report_service.get_context_summary(report)

        # Check if session notes are being generated
        update_generation_status = report.is_generating

        # Check if any audio or document inputs are being processed
        any_inputs_processing = (
                audio_inputs.filter(processing_successful=None).exists()
                or document_inputs.filter(processing_successful=None).exists()
        )

        if request.headers.get("HX-Request") and bool(request.GET.get("update_generation_status", False)):
            return render(
                request,
                "partials/report_card.html",
                {
                    "report": report,
                    "report_content": report.content,
                    "update_generation_status": update_generation_status,
                },
            )

        if request.headers.get("HX-Request") and bool(request.GET.get("update_session_material", False)):
            return render(
                request,
                "partials/input_display_with_material_report_ready.html",
                {
                    "session": report,
                    "any_inputs_processing": any_inputs_processing,
                    "audio_inputs": audio_inputs,
                    "document_inputs": document_inputs,
                },
            )

        return render(
            request,
            "reports/report_detail.html",
            {
                "report": report,
                "update_generation_status": update_generation_status,
                "any_inputs_processing": any_inputs_processing,
                "audio_inputs": audio_inputs,
                "document_inputs": document_inputs,
                "report_templates": report_templates,
                "audio_form": audio_form,
                "document_file_form": document_file_form,
                "document_text_form": document_text_form,
                "content_form": content_form,
                "context_summary": context_summary,
            },
        )

    def create(self, request):
        """Create a new report"""
        if request.method == "GET":
            form = ReportForm(user=request.user)

            # Check if this is a modal request (from dashboard)
            if request.headers.get("HX-Request") or request.GET.get("modal"):
                return render(request, "reports/report_form_modal.html", {"form": form})

            return render(request, "reports/report_form.html", {"form": form})

        elif request.method == "POST":
            form = ReportForm(request.POST, user=request.user)
            if form.is_valid():
                # Save the report first with empty content
                report = form.save(commit=False)
                report.content = ""
                report.save()  # UserFormMixin handles setting the user

                messages.success(request, "Bericht wurde erfolgreich erstellt.")

                # Check if this is a modal/HTMX request
                if request.headers.get("HX-Request") or request.POST.get("modal"):
                    from django.http import HttpResponse

                    # Return JavaScript to close modal and redirect
                    response = HttpResponse()
                    response["HX-Trigger"] = "closeModal"
                    response["HX-Redirect"] = f"/reports/{report.pk}/"
                    return response

                # Redirect to detail view for context input
                return redirect("reports:report_detail", pk=report.pk)

            # Check if this is a modal request for error handling
            if request.headers.get("HX-Request") or request.POST.get("modal"):
                return render(request, "reports/report_form_modal.html", {"form": form})

            return render(request, "reports/report_form.html", {"form": form})

    def update(self, request, pk=None):
        """Update an existing report"""
        # CRITICAL SECURITY: Only allow access to user's own reports
        report = get_object_or_404(Report, pk=pk, user=request.user)

        if request.method == "GET":
            form = ReportForm(instance=report, user=request.user)
            return render(request, "reports/report_form.html", {"form": form, "report": report})

        elif request.method == "POST":
            form = ReportForm(request.POST, instance=report, user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Bericht wurde erfolgreich aktualisiert.")
                return redirect("reports:report_detail", pk=report.pk)

            return render(request, "reports/report_form.html", {"form": form, "report": report})

    def destroy(self, request, pk=None):
        """Delete a report"""
        # CRITICAL SECURITY: Only allow access to user's own reports
        report = get_object_or_404(Report, pk=pk, user=request.user)

        if request.method == "GET":
            return render(request, "reports/report_confirm_delete.html", {"report": report})

        elif request.method == "POST":
            report.delete()
            messages.success(request, "Bericht wurde erfolgreich gelöscht.")
            return redirect("core:dashboard")

    @action(detail=True, methods=["post"])
    @method_decorator(csrf_exempt)
    def generate_content(self, request, pk=None):
        """Generate report content using AI in background task"""
        # CRITICAL SECURITY: Only allow access to user's own reports
        report = get_object_or_404(Report, pk=pk, user=request.user)
        
        try:
            data = json.loads(request.body)
            template_id = data.get('template_id')
            
            if not template_id:
                return JsonResponse({'error': 'Template-ID ist erforderlich'}, status=400)

            if report.is_generating:
                return JsonResponse({"error": "Bericht wird bereits generiert"}, status=400)

            generate_report_content_task.delay(
                report_id=report.id, template_id=int(template_id), user_id=request.user.id
            )

            return JsonResponse(
                {
                    "success": True,
                    "message": "Berichtgenerierung wurde gestartet. Die Seite wird automatisch aktualisiert.",
                }
            )
            
        except Exception as e:
            logger.error(f"Error starting report content generation: {str(e)}")
            return JsonResponse(
                {"error": f"Fehler beim Starten der Generierung: {str(e)}"}, status=500
            )

    @action(detail=True, methods=["post"])
    @method_decorator(csrf_exempt)
    def save_content(self, request, pk=None):
        """Save report content"""
        # CRITICAL SECURITY: Only allow access to user's own reports
        report = get_object_or_404(Report, pk=pk, user=request.user)
        
        try:
            content = request.POST.get('content', '')
            report.content = content
            report.save()
            
            if request.headers.get("HX-Request"):
                return HttpResponse("")  # Empty response for HTMX auto-save
            else:
                messages.success(request, "Berichtinhalt wurde erfolgreich gespeichert.")
                return redirect("reports:report_detail", pk=report.pk)
                
        except Exception as e:
            logger.error(f"Error saving content: {str(e)}")
            if request.headers.get("HX-Request"):
                return HttpResponse("", status=500)
            else:
                messages.error(request, f"Fehler beim Speichern: {str(e)}")
                return redirect("reports:report_detail", pk=report.pk)

    @action(detail=True, methods=["post"])
    @method_decorator(csrf_exempt)
    def create_from_template(self, request, pk=None):
        """Create report content from a template without context files"""
        # CRITICAL SECURITY: Only allow access to user's own reports
        report = get_object_or_404(Report, pk=pk, user=request.user)

        try:
            template_id = request.POST.get("template")

            if not template_id:
                messages.error(request, "Template ist erforderlich")
                return redirect("reports:report_detail", pk=report.pk)

            try:
                template = DocumentTemplate.objects.get_template(
                    int(template_id), DocumentTemplate.TemplateType.REPORT, user=request.user
                )
            except Exception:
                messages.error(request, "Template nicht gefunden")
                return redirect("reports:report_detail", pk=report.pk)

            # Use the template's user_prompt as the structure for report content
            # This is the template structure that will be filled out manually
            report.content = template.user_prompt
            report.save()

            messages.success(request, f"Vorlage '{template.name}' wurde erfolgreich angewendet.")

        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Berichts aus Template: {str(e)}")
            messages.error(request, f"Fehler beim Erstellen des Berichts: {str(e)}")

        return redirect("reports:report_detail", pk=report.pk)

    @action(detail=True, methods=["post"])
    @method_decorator(csrf_exempt)
    def export_pdf(self, request, pk=None):
        """Export report content to PDF"""
        # CRITICAL SECURITY: Only allow access to user's own reports
        report = get_object_or_404(Report, pk=pk, user=request.user)

        try:
            # Use the export service with database content
            from core.services import PDFExportService

            export_service = PDFExportService()

            # Prepare title
            title = report.title

            pdf_data = export_service.export_notes_to_pdf(
                title=title,
                date=report.created_at,
                content=report.content,
                filename_prefix="Bericht",
            )

            report.mark_as_exported()

            # Create Django response
            response = HttpResponse(pdf_data["content"], content_type=pdf_data["content_type"])
            response["Content-Disposition"] = f"attachment; filename={pdf_data['filename']}"

            return response

        except ValueError as e:
            messages.error(request, str(e))
            return redirect("reports:report_detail", pk=report.pk)
        except Exception as e:
            logger.error(f"Fehler beim Exportieren des Berichts als PDF: {str(e)}")
            messages.error(request, f"Fehler beim Exportieren des Berichts als PDF: {str(e)}")
            return redirect("reports:report_detail", pk=report.pk)
