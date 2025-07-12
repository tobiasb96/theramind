from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from rest_framework import viewsets
from rest_framework.decorators import action
import json

from .models import Document
from .forms import DocumentForm
from .services import DocumentService
from .prompts import get_available_document_types
from patients.models import Patient
from therapy.models import Therapy


class DocumentViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing document CRUD operations and custom actions.
    """

    def get_queryset(self):
        return Document.objects.select_related("therapy__patient").order_by("-created_at")

    def list(self, request):
        """List all documents"""
        documents = self.get_queryset()

        # Handle pagination
        paginator = Paginator(documents, 20)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(
            request,
            "documents/document_list.html",
            {
                "documents": page_obj,
                "page_obj": page_obj,
            },
        )

    def retrieve(self, request, pk=None):
        """Retrieve a specific document"""
        document = get_object_or_404(Document, pk=pk)

        return render(
            request,
            "documents/document_detail.html",
            {
                "document": document,
                "document_types": get_available_document_types(),
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

            return render(request, "documents/document_form.html", {"form": form})

        elif request.method == "POST":
            form = DocumentForm(request.POST)
            if form.is_valid():
                # Save the document first without content
                document = form.save(commit=False)
                document.content = ""  # Start with empty content
                document.save()
                form.save_m2m()  # Save many-to-many relationships

                # Generate AI content
                try:
                    document_service = DocumentService()
                    if document_service.is_available():
                        generated_content = document_service.generate(
                            document.therapy.patient, document.therapy, document.document_type
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

            return render(request, "documents/document_form.html", {"form": form})

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

            # Regular form update
            form = DocumentForm(request.POST, instance=document)
            if form.is_valid():
                form.save()
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

            return render(
                request, "documents/document_form.html", {"form": form, "document": document}
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
        document_text += f"Typ: {document.get_document_type_display()}\n"
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
            document_type = data.get("document_type")

            if not document_type:
                return JsonResponse({"error": "Dokumenttyp ist erforderlich"}, status=400)

            # Generate document using DocumentService
            document_service = DocumentService()
            if not document_service.is_available():
                return JsonResponse({"error": "OpenAI API Key ist nicht konfiguriert"}, status=400)

            generated_content = document_service.generate(patient, therapy, document_type)

            # Get document type name for title
            document_types = get_available_document_types()
            document_type_name = document_types.get(document_type, document_type)

            # Create document
            document = Document.objects.create(
                therapy=therapy,
                title=f"{document_type_name} - {patient.full_name}",
                content=generated_content,
                document_type=document_type,
            )

            return JsonResponse(
                {"success": True, "document_id": document.pk, "content": generated_content}
            )

        except Exception as e:
            return JsonResponse(
                {"error": f"Fehler bei der Dokumentgenerierung: {str(e)}"}, status=400
            )
