from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django_tables2 import RequestConfig
from django.db.models import Q
from itertools import chain
from reports.models import Report
from therapy_sessions.models import Session
from core.tables import BaseDocumentTable
from reports.services import TemplateService


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        recent_reports = Report.objects.filter(user=self.request.user).order_by("-created_at")[:8]
        recent_sessions = Session.objects.filter(user=self.request.user).order_by("-created_at")[:8]
        recent_documents = sorted(
            chain(recent_reports, recent_sessions), key=lambda doc: doc.created_at, reverse=True
        )[:8]

        table = BaseDocumentTable(recent_documents)
        RequestConfig(self.request, paginate=False).configure(table)
        context["recent_documents_table"] = table

        template_service = TemplateService()
        context["report_templates"] = template_service.get_document_templates(user=self.request.user)

        return context


class QuickSessionCreateView(LoginRequiredMixin, View):
    """Quick session creation from dashboard"""

    def post(self, request):
        try:
            title = request.POST.get("title", "")
            date = request.POST.get("date")
            patient_gender = request.POST.get("patient_gender", "not_specified")

            # Create the session
            session = Session.objects.create(
                user=request.user,
                date=date,
                title=title,
                patient_gender=patient_gender,
            )

            messages.success(request, "Sitzung wurde erfolgreich erstellt.")

            # Redirect to session detail
            return redirect("sessions:session_detail", pk=session.pk)

        except Exception as e:
            messages.error(request, f"Fehler beim Erstellen der Sitzung: {str(e)}")
            return redirect("core:dashboard")


class QuickDocumentCreateView(LoginRequiredMixin, View):
    """Quick document creation from dashboard"""

    def post(self, request):
        try:
            title = request.POST.get("title")
            patient_gender = request.POST.get("patient_gender", "not_specified")
            report = Report.objects.create(
                user=request.user,
                title=title,
                patient_gender=patient_gender,
            )
            return redirect("reports:report_detail", pk=report.pk)

        except Exception as e:
            messages.error(request, f"Fehler beim Erstellen des Berichts: {str(e)}")
            return redirect("core:dashboard")