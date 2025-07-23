from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_tables2 import RequestConfig
from itertools import chain
from reports.models import Report
from therapy_sessions.models import Session
from core.tables import BaseDocumentTable


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

        return context
