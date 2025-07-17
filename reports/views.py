from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from django_tables2 import RequestConfig
import json

from document_templates.models import DocumentTemplate

from .models import Report
from .forms import ReportForm
from .services import ReportService, TemplateService

from .tables import ReportTable
from therapy_sessions.models import Session


class ReportViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing report CRUD operations and custom actions.
    """

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
        """Retrieve a specific report"""
        report = get_object_or_404(Report, pk=pk)

        # Get available templates for report editing
        template_service = TemplateService()
        report_templates = template_service.get_document_templates()

        return render(
            request,
            "reports/report_detail.html",
            {
                "report": report,
                "report_templates": report_templates,
            },
        )

    def create(self, request):
        """Create a new report"""
        if request.method == "GET":
            form = ReportForm()

            # Get available templates for report creation
            template_service = TemplateService()
            report_templates = template_service.get_document_templates()

            return render(
                request,
                "reports/report_form.html",
                {
                    "form": form,
                    "report_templates": report_templates,
                },
            )

        elif request.method == "POST":
            form = ReportForm(request.POST)
            if form.is_valid():
                # Save the report first without content
                report = form.save(commit=False)
                report.content = ""  # Start with empty content
                report.save()
                form.save_m2m()

                # Generate AI content with selected template
                try:
                    report_service = ReportService()
                    if report_service.is_available():
                        template_id = request.POST.get("template_id")
                        generated_content = report_service.generate(
                            template_id=int(template_id) if template_id else None,
                        )
                        report.content = generated_content
                        report.save()
                        messages.success(
                            request,
                            "Bericht wurde erfolgreich erstellt und mit KI-Inhalt generiert.",
                        )
                    else:
                        messages.warning(
                            request,
                            "Bericht wurde erstellt, aber KI-Generierung ist nicht verfügbar. Bitte fügen Sie den Inhalt manuell hinzu.",
                        )
                except Exception as e:
                    messages.warning(
                        request,
                        f"Bericht wurde erstellt, aber KI-Generierung fehlgeschlagen: {str(e)}. Bitte fügen Sie den Inhalt manuell hinzu.",
                    )

                return HttpResponse(
                    status=302,
                    headers={
                        "Location": reverse_lazy(
                            "reports:report_detail", kwargs={"pk": report.pk}
                        )
                    },
                )

            # If form is invalid, get templates again
            template_service = TemplateService()
            templates = template_service.get_document_templates()

            return render(
                request,
                "reports/report_form.html",
                {
                    "form": form,
                    "report_templates": templates,
                },
            )

    def update(self, request, pk=None):
        """Update an existing report (handles both form data and content updates)"""
        report = get_object_or_404(Report, pk=pk)

        if request.method == "GET":
            form = ReportForm(instance=report)
            return render(
                request, "reports/report_form.html", {"form": form, "report": report}
            )

        elif request.method == "POST":
            # Check if this is a content-only update (from report detail page)
            if (
                "content" in request.POST and len(request.POST) == 2
            ):  # content + csrfmiddlewaretoken
                try:
                    content = request.POST.get("content", "")
                    report.content = content
                    report.save()

                    messages.success(request, "Berichtinhalt wurde erfolgreich gespeichert.")

                    # Handle HTMX requests
                    if request.headers.get("HX-Request"):
                        response = HttpResponse()
                        response["HX-Redirect"] = reverse_lazy(
                            "reports:report_detail", kwargs={"pk": report.pk}
                        )
                        return response

                    return HttpResponse(
                        status=302,
                        headers={
                            "Location": reverse_lazy(
                                "reports:report_detail", kwargs={"pk": report.pk}
                            )
                        },
                    )

                except Exception as e:
                    messages.error(request, f"Fehler beim Speichern: {str(e)}")
                    return HttpResponse(
                        status=302,
                        headers={
                            "Location": reverse_lazy(
                                "reports:report_detail", kwargs={"pk": report.pk}
                            )
                        },
                    )

            # Regular form update (from edit modal)
            # Handle template and sessions fields
            request.POST.get("template_id")
            sessions_ids = request.POST.getlist("sessions")

            # Update basic fields
            report.title = request.POST.get("title", report.title)
            report.save()

            # Update sessions
            if sessions_ids:
                sessions = Session.objects.filter(pk__in=sessions_ids)
                report.sessions.set(sessions)
            else:
                report.sessions.clear()

            messages.success(request, "Bericht wurde erfolgreich aktualisiert.")

            # Handle HTMX requests
            if request.headers.get("HX-Request"):
                response = HttpResponse()
                response["HX-Redirect"] = reverse_lazy(
                    "reports:report_detail", kwargs={"pk": report.pk}
                )
                return response

            return HttpResponse(
                status=302,
                headers={
                    "Location": reverse_lazy(
                        "reports:report_detail", kwargs={"pk": report.pk}
                    )
                },
            )

    def destroy(self, request, pk=None):
        """Delete a report"""
        report = get_object_or_404(Report, pk=pk)

        if request.method == "GET":
            return render(request, "reports/report_confirm_delete.html", {"report": report})

        elif request.method == "POST":
            report.delete()
            messages.success(request, "Bericht wurde erfolgreich gelöscht.")

            # Handle HTMX requests
            if request.headers.get("HX-Request"):
                response = HttpResponse()
                response["HX-Redirect"] = reverse_lazy("reports:reports_list")
                return response

            return HttpResponse(
                status=302, headers={"Location": reverse_lazy("reports:reports_list")}
            )

    @action(detail=True, methods=["get"])
    def export(self, request, pk=None):
        """Export report as text file"""
        report = get_object_or_404(Report, pk=pk)

        report_text = f"{report.title}\n\n"
        report_text += f"Datum: {report.created_at.strftime('%d.%m.%Y')}\n"
        if report.updated_at != report.created_at:
            report_text += f"Aktualisiert: {report.updated_at.strftime('%d.%m.%Y %H:%M')}\n"
        report_text += f"\n{report.content}\n"

        # Create filename
        filename = f"{report.title.replace(' ', '_').replace('/', '_').lower()}.txt"

        # Create response
        response = HttpResponse(report_text, content_type="text/plain; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response

    @action(detail=False, methods=["post"])
    @method_decorator(csrf_exempt)
    def generate(self, request):
        """Generate report using AI"""
        try:
            data = json.loads(request.body)
            template_id = data.get("template_id")

            # Generate report using ReportService
            report_service = ReportService()
            if not report_service.is_available():
                return JsonResponse({"error": "OpenAI API Key ist nicht konfiguriert"}, status=400)

            generated_content = report_service.generate(template_id=template_id)

            # Create report
            template = DocumentTemplate.objects.get(pk=template_id)
            report = Report.objects.create(
                title=f"Bericht {template.name}",
                content=generated_content,
            )

            return JsonResponse(
                {"success": True, "report_id": report.pk, "content": generated_content}
            )

        except Exception as e:
            return JsonResponse(
                {"error": f"Fehler bei der Berichtgenerierung: {str(e)}"}, status=400
            )
