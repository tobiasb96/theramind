from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django_tables2 import RequestConfig
from reports.models import Document
from reports.tables import DocumentTable
from reports.services import TemplateService, ReportService
from sessions.models import Session


class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get recent documents for table display
        recent_documents = Document.objects.order_by("-created_at")[:10]

        # Create table for recent documents (convert to list to avoid queryset ordering issues)
        table = DocumentTable(list(recent_documents))
        RequestConfig(self.request, paginate=False).configure(table)
        context["recent_documents_table"] = table

        # Get document templates for quick document creation
        template_service = TemplateService()
        context["document_templates"] = template_service.get_document_templates()

        return context


class QuickSessionCreateView(View):
    """Quick session creation from dashboard"""

    def post(self, request):
        try:
            title = request.POST.get("title", "")
            date = request.POST.get("date")
            duration = int(request.POST.get("duration", 50))

            # Create the session
            session = Session.objects.create(
                date=date,
                duration=duration,
                title=title,
            )

            messages.success(request, "Sitzung wurde erfolgreich erstellt.")

            # Redirect to session detail
            return redirect("sessions:session_detail", session_pk=session.pk)

        except Exception as e:
            messages.error(request, f"Fehler beim Erstellen der Sitzung: {str(e)}")
            return redirect("core:dashboard")


class QuickDocumentCreateView(View):
    """Quick document creation from dashboard"""

    def post(self, request):
        try:
            title = request.POST.get("title")
            template_id = request.POST.get("template_id")

            # Create the document first without content
            document = Document.objects.create(
                title=title,
                content="",
            )

            # Generate AI content with selected template
            try:
                document_service = ReportService()
                if document_service.is_available():
                    template_id_int = int(template_id) if template_id else None
                    generated_content = document_service.generate(template_id=template_id_int)
                    document.content = generated_content
                    document.save()
                    messages.success(
                        request,
                        "Dokument wurde erfolgreich erstellt und mit KI-Inhalt generiert.",
                    )
                else:
                    messages.warning(
                        request,
                        "Dokument wurde erstellt, aber KI-Generierung ist nicht verfügbar. Bitte fügen Sie den Inhalt manuell hinzu.",
                    )
            except Exception as e:
                messages.warning(
                    request,
                    f"Dokument wurde erstellt, aber KI-Generierung fehlgeschlagen: {str(e)}. Bitte fügen Sie den Inhalt manuell hinzu.",
                )

            # Redirect to document detail
            return redirect("documents:document_detail", pk=document.pk)

        except Exception as e:
            messages.error(request, f"Fehler beim Erstellen des Dokuments: {str(e)}")
            return redirect("core:dashboard")