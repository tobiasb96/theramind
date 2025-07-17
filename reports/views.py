from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_tables2 import RequestConfig
import json
import logging

from document_templates.models import DocumentTemplate
from document_templates.service import TemplateService

from .models import Report, ReportContextFile
from .forms import ReportForm, ReportContextFileForm, ReportContextTextForm, ReportContentForm
from .services import ReportService
from .tables import ReportTable

logger = logging.getLogger(__name__)


class ReportViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing report CRUD operations and custom actions.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Report.objects.order_by("-created_at")

    def list(self, request):
        """List all reports"""
        reports = self.get_queryset()

        # Handle search
        search_query = request.GET.get("search", "")
        if search_query:
            reports = reports.filter(Q(title__icontains=search_query))
        
        # Create table with proper ordering
        table = ReportTable(reports)
        RequestConfig(request, paginate={"per_page": 20}).configure(table)

        return render(
            request,
            "reports/reports_list.html",
            {
                "reports_table": table,
                "search_query": search_query,
            },
        )

    def retrieve(self, request, pk=None):
        """Retrieve a specific report detail view"""
        report = get_object_or_404(Report, pk=pk)
        
        # Get context files
        context_files = report.context_files.filter(extraction_successful=True).order_by(
            "-created_at"
        )
        
        # Get available templates for report generation
        template_service = TemplateService()
        report_templates = template_service.get_available_templates(
            DocumentTemplate.TemplateType.REPORT
        )
        
        # Initialize forms
        file_form = ReportContextFileForm()
        text_form = ReportContextTextForm()
        content_form = ReportContentForm(instance=report)
        
        # Get context summary
        report_service = ReportService()
        context_summary = report_service.get_context_summary(report)

        return render(
            request,
            "reports/report_detail.html",
            {
                "report": report,
                "context_files": context_files,
                "report_templates": report_templates,
                "file_form": file_form,
                "text_form": text_form,
                "content_form": content_form,
                "context_summary": context_summary,
            },
        )

    def create(self, request):
        """Create a new report"""
        if request.method == "GET":
            form = ReportForm()
            return render(request, "reports/report_form.html", {"form": form})

        elif request.method == "POST":
            form = ReportForm(request.POST)
            if form.is_valid():
                # Save the report first with empty content
                report = form.save(commit=False)
                report.content = ""
                report.save()

                messages.success(request, "Bericht wurde erfolgreich erstellt.")
                
                # Redirect to detail view for context input
                return redirect("reports:report_detail", pk=report.pk)

            return render(request, "reports/report_form.html", {"form": form})

    def update(self, request, pk=None):
        """Update an existing report"""
        report = get_object_or_404(Report, pk=pk)

        if request.method == "GET":
            form = ReportForm(instance=report)
            return render(request, "reports/report_form.html", {"form": form, "report": report})

        elif request.method == "POST":
            form = ReportForm(request.POST, instance=report)
            if form.is_valid():
                form.save()
                messages.success(request, "Bericht wurde erfolgreich aktualisiert.")
                return redirect("reports:report_detail", pk=report.pk)

            return render(request, "reports/report_form.html", {"form": form, "report": report})

    def destroy(self, request, pk=None):
        """Delete a report"""
        report = get_object_or_404(Report, pk=pk)

        if request.method == "GET":
            return render(request, "reports/report_confirm_delete.html", {"report": report})

        elif request.method == "POST":
            report.delete()
            messages.success(request, "Bericht wurde erfolgreich gelöscht.")
            return redirect("reports:reports_list")

    @action(detail=True, methods=["post"])
    @method_decorator(csrf_exempt)
    def upload_context_file(self, request, pk=None):
        """Upload a context file to a report"""
        report = get_object_or_404(Report, pk=pk)
        
        if 'original_file' not in request.FILES:
            messages.error(request, "Keine Datei hochgeladen")
            return redirect("reports:report_detail", pk=report.pk)
        
        uploaded_file = request.FILES['original_file']
        
        try:
            # Use report service to add context file
            report_service = ReportService()
            context_file = report_service.add_context_file(report, uploaded_file)
            
            if context_file.extraction_successful:
                messages.success(
                    request, 
                    f"Datei '{context_file.file_name}' wurde erfolgreich hochgeladen und verarbeitet."
                )
            else:
                messages.warning(
                    request,
                    f"Datei '{context_file.file_name}' wurde hochgeladen, aber die Textextraktion fehlgeschlagen: {context_file.extraction_error}"
                )
                
        except Exception as e:
            logger.error(f"Error uploading context file: {str(e)}")
            messages.error(request, f"Fehler beim Hochladen der Datei: {str(e)}")
        
        return redirect("reports:report_detail", pk=report.pk)

    @action(detail=True, methods=["post"])
    @method_decorator(csrf_exempt)
    def add_context_text(self, request, pk=None):
        """Add manual text as context to a report"""
        report = get_object_or_404(Report, pk=pk)
        
        form = ReportContextTextForm(request.POST)
        if form.is_valid():
            try:
                # Use report service to add context text
                report_service = ReportService()
                context_file = report_service.add_context_text(
                    report=report,
                    text=form.cleaned_data['text_input'],
                    file_name=form.cleaned_data['file_name']
                )
                
                messages.success(
                    request, 
                    f"Text '{context_file.file_name}' wurde erfolgreich hinzugefügt."
                )
                
            except Exception as e:
                logger.error(f"Error adding context text: {str(e)}")
                messages.error(request, f"Fehler beim Hinzufügen des Texts: {str(e)}")
        else:
            messages.error(request, "Ungültige Eingabe. Bitte prüfen Sie die Eingaben.")
        
        return redirect("reports:report_detail", pk=report.pk)

    @action(detail=True, methods=["post"])
    @method_decorator(csrf_exempt)
    def delete_context_file(self, request, pk=None):
        """Delete a context file from a report"""
        report = get_object_or_404(Report, pk=pk)
        
        try:
            data = json.loads(request.body)
            context_file_id = data.get('context_file_id')
            
            if not context_file_id:
                return JsonResponse({'error': 'Kontext-Datei-ID fehlt'}, status=400)
            
            context_file = get_object_or_404(ReportContextFile, id=context_file_id, report=report)
            file_name = context_file.file_name
            context_file.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Kontext-Datei "{file_name}" wurde erfolgreich gelöscht.'
            })
            
        except Exception as e:
            logger.error(f"Error deleting context file: {str(e)}")
            return JsonResponse({'error': f'Fehler beim Löschen: {str(e)}'}, status=500)

    @action(detail=True, methods=["post"])
    @method_decorator(csrf_exempt)
    def generate_content(self, request, pk=None):
        """Generate report content using AI"""
        report = get_object_or_404(Report, pk=pk)
        
        try:
            data = json.loads(request.body)
            template_id = data.get('template_id')
            
            if not template_id:
                return JsonResponse({'error': 'Template-ID ist erforderlich'}, status=400)
            
            # Generate content using ReportService
            report_service = ReportService()
            if not report_service.is_available():
                return JsonResponse({'error': 'KI-Service ist nicht verfügbar'}, status=400)
            
            generated_content = report_service.generate(report, template_id=int(template_id))
            
            # Update report content
            report.content = generated_content
            report.save()
            
            return JsonResponse({
                'success': True,
                'content': generated_content,
                'message': 'Berichtinhalt wurde erfolgreich generiert.'
            })
            
        except Exception as e:
            logger.error(f"Error generating report content: {str(e)}")
            return JsonResponse({'error': f'Fehler bei der Generierung: {str(e)}'}, status=500)

    @action(detail=True, methods=["post"])
    @method_decorator(csrf_exempt)
    def save_content(self, request, pk=None):
        """Save report content"""
        report = get_object_or_404(Report, pk=pk)
        
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
        report = get_object_or_404(Report, pk=pk)

        try:
            template_id = request.POST.get("template")

            if not template_id:
                messages.error(request, "Template ist erforderlich")
                return redirect("reports:report_detail", pk=report.pk)

            # Get the template
            try:
                template = DocumentTemplate.objects.get(
                    id=template_id, template_type=DocumentTemplate.TemplateType.REPORT
                )
            except DocumentTemplate.DoesNotExist:
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
        report = get_object_or_404(Report, pk=pk)

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
