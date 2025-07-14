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

from .models import Document, DocumentTemplate
from .forms import DocumentForm
from .services import DocumentService, TemplateService

from .tables import DocumentTable
from patients.models import Patient
from therapy.models import Therapy


class TemplateViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing custom templates
    """

    def get_queryset(self):
        # TODO: Filter by user when user model is implemented
        return DocumentTemplate.objects.filter(is_active=True).order_by("name")

    def list(self, request):
        """List all templates"""
        template_type = request.GET.get("type", "document")
        templates = self.get_queryset().filter(template_type=template_type)

        # Handle search
        search_query = request.GET.get("search", "")
        if search_query:
            templates = templates.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        return render(
            request,
            "documents/template_list.html",
            {
                "templates": templates,
                "template_type": template_type,
                "search_query": search_query,
            },
        )

    def retrieve(self, request, pk=None):
        """Retrieve a specific template"""
        template = get_object_or_404(DocumentTemplate, pk=pk)

        return render(
            request,
            "documents/template_detail.html",
            {"template": template},
        )

    def create(self, request):
        """Create a new template"""
        if request.method == "GET":
            # Show template creation form
            return render(
                request,
                "documents/template_form.html",
                {
                    "template_types": DocumentTemplate.TEMPLATE_TYPES,
                },
            )

        elif request.method == "POST":
            # Create new template
            try:
                template_data = {
                    "name": request.POST.get("name"),
                    "description": request.POST.get("description", ""),
                    "template_type": request.POST.get("template_type"),
                    "system_prompt": "",  # Always empty, hardcoded in service
                    "user_prompt": request.POST.get("user_prompt"),
                    "max_tokens": int(request.POST.get("max_tokens", 2000)),
                    "temperature": float(request.POST.get("temperature", 0.3)),
                    "is_predefined": False,
                    "is_active": True,
                }

                template_service = TemplateService()
                # TODO: Pass user_id when user model is implemented
                template = template_service.create_custom_template(template_data)

                messages.success(request, "Template wurde erfolgreich erstellt.")
                return HttpResponse(
                    status=302,
                    headers={
                        "Location": reverse_lazy(
                            "documents:template_detail", kwargs={"pk": template.pk}
                        )
                    },
                )

            except Exception as e:
                messages.error(request, f"Fehler beim Erstellen des Templates: {str(e)}")
                return render(
                    request,
                    "documents/template_form.html",
                    {
                        "template_types": DocumentTemplate.TEMPLATE_TYPES,
                    },
                )

    def update(self, request, pk=None):
        """Update an existing template"""
        template = get_object_or_404(DocumentTemplate, pk=pk)

        if request.method == "GET":
            return render(
                request,
                "documents/template_form.html",
                {
                    "template": template,
                    "template_types": DocumentTemplate.TEMPLATE_TYPES,
                },
            )

        elif request.method == "POST":
            try:
                template.name = request.POST.get("name")
                template.description = request.POST.get("description", "")
                template.template_type = request.POST.get("template_type")
                template.document_type = request.POST.get("document_type") or None
                template.user_prompt = request.POST.get("user_prompt")
                template.max_tokens = int(request.POST.get("max_tokens", 2000))
                template.temperature = float(request.POST.get("temperature", 0.3))
                template.save()

                messages.success(request, "Template wurde erfolgreich aktualisiert.")
                return HttpResponse(
                    status=302,
                    headers={
                        "Location": reverse_lazy(
                            "documents:template_detail", kwargs={"pk": template.pk}
                        )
                    },
                )

            except Exception as e:
                messages.error(request, f"Fehler beim Aktualisieren des Templates: {str(e)}")
                return render(
                    request,
                    "documents/template_form.html",
                    {
                        "template": template,
                        "template_types": DocumentTemplate.TEMPLATE_TYPES,
                        "document_types": Document.DOCUMENT_TYPES,
                    },
                )

    def destroy(self, request, pk=None):
        """Delete a template"""
        template = get_object_or_404(DocumentTemplate, pk=pk)

        if request.method == "GET":
            return render(request, "documents/template_confirm_delete.html", {"template": template})

        elif request.method == "POST":
            template.delete()
            messages.success(request, "Template wurde erfolgreich gelöscht.")

            # Handle HTMX requests
            if request.headers.get("HX-Request"):
                response = HttpResponse()
                response["HX-Redirect"] = reverse_lazy("documents:template_list")
                return response

            return HttpResponse(
                status=302, headers={"Location": reverse_lazy("documents:template_list")}
            )

    @action(detail=True, methods=["post"])
    def clone(self, request, pk=None):
        """Clone a template"""
        template = get_object_or_404(DocumentTemplate, pk=pk)

        try:
            new_name = request.POST.get("name", f"{template.name} (Kopie)")

            template_service = TemplateService()
            # TODO: Pass user_id when user model is implemented
            cloned_template = template_service.clone_template(template.id, new_name)

            messages.success(request, f"Template '{new_name}' wurde erfolgreich erstellt.")
            return HttpResponse(
                status=302,
                headers={
                    "Location": reverse_lazy(
                        "documents:template_detail", kwargs={"pk": cloned_template.pk}
                    )
                },
            )

        except Exception as e:
            messages.error(request, f"Fehler beim Klonen des Templates: {str(e)}")
            return HttpResponse(
                status=302,
                headers={
                    "Location": reverse_lazy(
                        "documents:template_detail", kwargs={"pk": template.pk}
                    )
                },
            )


class DocumentViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing document CRUD operations and custom actions.
    """

    def get_queryset(self):
        return Document.objects.select_related("therapy__patient").order_by("-created_at")

    def list(self, request):
        """List all documents"""
        documents = self.get_queryset()

        # Handle search
        search_query = request.GET.get("search", "")
        if search_query:
            documents = documents.filter(
                Q(title__icontains=search_query)
                | Q(therapy__patient__first_name__icontains=search_query)
                | Q(therapy__patient__last_name__icontains=search_query)
            )
        # Create table with proper ordering
        table = DocumentTable(documents)
        RequestConfig(request, paginate={"per_page": 20}).configure(table)

        return render(
            request,
            "documents/document_list.html",
            {
                "table": table,
                "search_query": search_query,
            },
        )

    def retrieve(self, request, pk=None):
        """Retrieve a specific document"""
        document = get_object_or_404(Document, pk=pk)

        # Get available templates for document editing
        template_service = TemplateService()
        document_templates = template_service.get_document_templates()

        return render(
            request,
            "documents/document_detail.html",
            {
                "document": document,
                "document_templates": document_templates,
            },
        )

    def create(self, request):
        """Create a new document"""
        if request.method == "GET":
            form = DocumentForm()

            # Pre-populate therapy if provided
            therapy_id = request.GET.get("therapy")
            if therapy_id:
                try:
                    therapy = Therapy.objects.get(pk=therapy_id)
                    form.initial["therapy"] = therapy
                except Therapy.DoesNotExist:
                    pass

            # Get available templates for document creation
            template_service = TemplateService()
            document_templates = template_service.get_document_templates()

            return render(
                request,
                "documents/document_form.html",
                {
                    "form": form,
                    "document_templates": document_templates,
                },
            )

        elif request.method == "POST":
            form = DocumentForm(request.POST)
            if form.is_valid():
                # Save the document first without content
                document = form.save(commit=False)
                document.content = ""  # Start with empty content
                document.save()
                form.save_m2m()

                # Generate AI content with selected template
                try:
                    document_service = DocumentService()
                    if document_service.is_available():
                        template_id = request.POST.get("template_id")
                        generated_content = document_service.generate(
                            document.therapy.patient,
                            document.therapy,
                            template_id=int(template_id) if template_id else None,
                        )
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

                return HttpResponse(
                    status=302,
                    headers={
                        "Location": reverse_lazy(
                            "documents:document_detail", kwargs={"pk": document.pk}
                        )
                    },
                )

            # If form is invalid, get templates again
            template_service = TemplateService()
            document_templates = template_service.get_document_templates()

            return render(
                request,
                "documents/document_form.html",
                {
                    "form": form,
                    "document_templates": document_templates,
                },
            )

    def update(self, request, pk=None):
        """Update an existing document (handles both form data and content updates)"""
        document = get_object_or_404(Document, pk=pk)

        if request.method == "GET":
            form = DocumentForm(instance=document)
            return render(
                request, "documents/document_form.html", {"form": form, "document": document}
            )

        elif request.method == "POST":
            # Check if this is a content-only update (from document detail page)
            if (
                "content" in request.POST and len(request.POST) == 2
            ):  # content + csrfmiddlewaretoken
                try:
                    content = request.POST.get("content", "")
                    document.content = content
                    document.save()

                    messages.success(request, "Dokumentinhalt wurde erfolgreich gespeichert.")

                    # Handle HTMX requests
                    if request.headers.get("HX-Request"):
                        response = HttpResponse()
                        response["HX-Redirect"] = reverse_lazy(
                            "documents:document_detail", kwargs={"pk": document.pk}
                        )
                        return response

                    return HttpResponse(
                        status=302,
                        headers={
                            "Location": reverse_lazy(
                                "documents:document_detail", kwargs={"pk": document.pk}
                            )
                        },
                    )

                except Exception as e:
                    messages.error(request, f"Fehler beim Speichern: {str(e)}")
                    return HttpResponse(
                        status=302,
                        headers={
                            "Location": reverse_lazy(
                                "documents:document_detail", kwargs={"pk": document.pk}
                            )
                        },
                    )

            # Regular form update (from edit modal)
            # Handle template and sessions fields
            template_id = request.POST.get("template_id")
            sessions_ids = request.POST.getlist("sessions")

            # Update basic fields
            document.title = request.POST.get("title", document.title)

            # Update therapy if provided
            therapy_id = request.POST.get("therapy")
            if therapy_id:
                try:
                    therapy = Therapy.objects.get(pk=therapy_id)
                    document.therapy = therapy
                except Therapy.DoesNotExist:
                    pass

            document.save()

            # Update sessions
            if sessions_ids:
                sessions = Session.objects.filter(pk__in=sessions_ids)
                document.sessions.set(sessions)
            else:
                document.sessions.clear()

            messages.success(request, "Dokument wurde erfolgreich aktualisiert.")

            # Handle HTMX requests
            if request.headers.get("HX-Request"):
                response = HttpResponse()
                response["HX-Redirect"] = reverse_lazy(
                    "documents:document_detail", kwargs={"pk": document.pk}
                )
                return response

            return HttpResponse(
                status=302,
                headers={
                    "Location": reverse_lazy(
                        "documents:document_detail", kwargs={"pk": document.pk}
                    )
                },
            )

    def destroy(self, request, pk=None):
        """Delete a document"""
        document = get_object_or_404(Document, pk=pk)

        if request.method == "GET":
            return render(request, "documents/document_confirm_delete.html", {"document": document})

        elif request.method == "POST":
            document.delete()
            messages.success(request, "Dokument wurde erfolgreich gelöscht.")

            # Handle HTMX requests
            if request.headers.get("HX-Request"):
                response = HttpResponse()
                response["HX-Redirect"] = reverse_lazy("documents:document_list")
                return response

            return HttpResponse(
                status=302, headers={"Location": reverse_lazy("documents:document_list")}
            )

    @action(detail=True, methods=["get"])
    def export(self, request, pk=None):
        """Export document as text file"""
        document = get_object_or_404(Document, pk=pk)

        # Create document content
        document_text = f"{document.title}\n\n"
        document_text += f"Patient: {document.therapy.patient.full_name}\n"
        document_text += f"Datum: {document.created_at.strftime('%d.%m.%Y')}\n"
        if document.updated_at != document.created_at:
            document_text += f"Aktualisiert: {document.updated_at.strftime('%d.%m.%Y %H:%M')}\n"
        document_text += f"\n{document.content}\n"

        # Create filename
        filename = f"{document.title.replace(' ', '_').replace('/', '_').lower()}.txt"

        # Create response
        response = HttpResponse(document_text, content_type="text/plain; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response

    @action(detail=False, methods=["post"])
    @method_decorator(csrf_exempt)
    def generate(self, request, patient_pk=None, therapy_pk=None):
        """Generate document using AI"""
        # Validate the nested relationship
        patient = get_object_or_404(Patient, pk=patient_pk)
        therapy = get_object_or_404(Therapy, pk=therapy_pk, patient=patient)

        try:
            data = json.loads(request.body)
            template_id = data.get("template_id")

            # Generate document using DocumentService
            document_service = DocumentService()
            if not document_service.is_available():
                return JsonResponse({"error": "OpenAI API Key ist nicht konfiguriert"}, status=400)

            generated_content = document_service.generate(patient, therapy, template_id=template_id)

            # Create document
            document = Document.objects.create(
                therapy=therapy,
                title=f"Dokument - {patient.full_name}",
                content=generated_content,
            )

            return JsonResponse(
                {"success": True, "document_id": document.pk, "content": generated_content}
            )

        except Exception as e:
            return JsonResponse(
                {"error": f"Fehler bei der Dokumentgenerierung: {str(e)}"}, status=400
            )
