from django.views.generic import TemplateView
from documents.models import Document
from patients.models import Patient
from therapy.models import Session


class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient_count'] = Patient.objects.count()
        context['session_count'] = Session.objects.count()

        # Get recent documents instead of sessions
        context["recent_documents"] = Document.objects.select_related("therapy__patient").order_by(
            "-created_at"
        )[:5]
        context['recent_patients'] = Patient.objects.order_by('-created_at')[:5]
        return context