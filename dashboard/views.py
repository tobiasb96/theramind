from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import redirect
from django.contrib import messages
from django_tables2 import RequestConfig
from reports.models import Report
from reports.tables import ReportTable
from reports.services import TemplateService
from therapy_sessions.models import Session


class DashboardView(TemplateView):
    template_name = "dashboard/dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get recent documents for table display
        recent_reports = Report.objects.order_by("-created_at")[:10]

        # Create table for recent documents (convert to list to avoid queryset ordering issues)
        table = ReportTable(list(recent_reports))
        RequestConfig(self.request, paginate=False).configure(table)
        context["recent_reports_table"] = table

        # Get document templates for quick document creation
        template_service = TemplateService()
        context["report_templates"] = template_service.get_document_templates()

        return context


class QuickSessionCreateView(View):
    """Quick session creation from dashboard"""

    def post(self, request):
        try:
            title = request.POST.get("title", "")
            date = request.POST.get("date")

            # Create the session
            session = Session.objects.create(
                date=date,
                title=title,
            )

            messages.success(request, "Sitzung wurde erfolgreich erstellt.")

            # Redirect to session detail
            return redirect("sessions:session_detail", pk=session.pk)

        except Exception as e:
            messages.error(request, f"Fehler beim Erstellen der Sitzung: {str(e)}")
            return redirect("core:dashboard")


class QuickDocumentCreateView(View):
    """Quick document creation from dashboard"""

    def post(self, request):
        try:
            title = request.POST.get("title")
            report = Report.objects.create(title=title)
            return redirect("reports:report_detail", pk=report.pk)

        except Exception as e:
            messages.error(request, f"Fehler beim Erstellen des Berichts: {str(e)}")
            return redirect("core:dashboard")