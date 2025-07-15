from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django_tables2 import RequestConfig
from documents.models import Document
from documents.tables import DocumentTable
from documents.services import TemplateService, DocumentService
from patients.models import Patient
from therapy.models import Session, Therapy


class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get recent documents for table display
        recent_documents = Document.objects.select_related("therapy__patient").order_by(
            "-created_at"
        )[:10]

        # Create table for recent documents (convert to list to avoid queryset ordering issues)
        table = DocumentTable(list(recent_documents))
        RequestConfig(self.request, paginate=False).configure(table)
        context["recent_documents_table"] = table

        # Get data for quick creation modals
        context["patients"] = Patient.objects.order_by("last_name", "first_name")

        # Get document templates for quick document creation
        template_service = TemplateService()
        context["document_templates"] = template_service.get_document_templates()

        return context


class QuickSessionCreateView(View):
    """Quick session creation from dashboard"""

    def post(self, request):
        try:
            patient_id = request.POST.get("patient")
            title = request.POST.get("title", "")
            date = request.POST.get("date")
            duration = int(request.POST.get("duration", 50))

            # Get or create patient
            patient = get_object_or_404(Patient, pk=patient_id)

            # Find or create an active therapy for this patient
            therapy = Therapy.objects.filter(patient=patient, status="active").first()
            if not therapy:
                therapy = Therapy.objects.create(
                    patient=patient,
                    title=f"Therapie für {patient.full_name}",
                    description="Automatisch erstellt",
                    status="active",
                )

            # Create the session
            session = Session.objects.create(
                therapy=therapy,
                date=date,
                duration=duration,
                title=title,
            )

            messages.success(
                request, f"Sitzung für {patient.full_name} wurde erfolgreich erstellt."
            )

            # Redirect to session detail
            return redirect(
                "therapy:session_detail",
                patient_pk=patient.pk,
                therapy_pk=therapy.pk,
                session_pk=session.pk,
            )

        except Exception as e:
            messages.error(request, f"Fehler beim Erstellen der Sitzung: {str(e)}")
            return redirect("core:dashboard")


class QuickDocumentCreateView(View):
    """Quick document creation from dashboard"""

    def post(self, request):
        try:
            patient_id = request.POST.get("patient")
            title = request.POST.get("title")
            template_id = request.POST.get("template_id")

            # Get patient
            patient = get_object_or_404(Patient, pk=patient_id)

            # Find or create an active therapy for this patient
            therapy = Therapy.objects.filter(patient=patient, status="active").first()
            if not therapy:
                therapy = Therapy.objects.create(
                    patient=patient,
                    title=f"Therapie für {patient.full_name}",
                    description="Automatisch erstellt",
                    status="active",
                )

            # Create the document first without content
            document = Document.objects.create(
                therapy=therapy,
                title=title,
                content="",
            )

            # Generate AI content with selected template
            try:
                document_service = DocumentService()
                if document_service.is_available():
                    template_id_int = int(template_id) if template_id else None
                    generated_content = document_service.generate(
                        patient, therapy, template_id=template_id_int
                    )
                    document.content = generated_content
                    document.save()
                    messages.success(
                        request,
                        f"Dokument für {patient.full_name} wurde erfolgreich erstellt und mit KI-Inhalt generiert.",
                    )
                else:
                    messages.warning(
                        request,
                        f"Dokument für {patient.full_name} wurde erstellt, aber KI-Generierung ist nicht verfügbar. Bitte fügen Sie den Inhalt manuell hinzu.",
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