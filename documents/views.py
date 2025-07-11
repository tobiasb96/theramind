from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Document
from .forms import DocumentForm
from .services import DocumentService
from .prompts import get_available_document_types
from core.models import Patient
from therapy.models import Therapy
import json


class DocumentListView(ListView):
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'
    paginate_by = 20
    
    def get_queryset(self):
        return Document.objects.select_related('therapy__patient').order_by('-created_at')


class DocumentDetailView(DetailView):
    model = Document
    template_name = 'documents/document_detail.html'
    context_object_name = 'document'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document_types'] = get_available_document_types()
        return context


class DocumentCreateView(CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        therapy_id = self.request.GET.get('therapy')
        if therapy_id:
            try:
                therapy = Therapy.objects.get(pk=therapy_id)
                initial['therapy'] = therapy
            except Therapy.DoesNotExist:
                pass
        return initial
    
    def get_success_url(self):
        return reverse_lazy('documents:document_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        # Save the document first without content
        self.object = form.save(commit=False)
        self.object.content = ""  # Start with empty content
        self.object.save()
        form.save_m2m()  # Save many-to-many relationships
        
        # Generate AI content
        try:
            document_service = DocumentService()
            if document_service.is_available():
                generated_content = document_service.generate(
                    self.object.therapy.patient, 
                    self.object.therapy, 
                    self.object.document_type
                )
                self.object.content = generated_content
                self.object.save()
                messages.success(self.request, 'Dokument wurde erfolgreich erstellt und mit KI-Inhalt generiert.')
            else:
                messages.warning(self.request, 'Dokument wurde erstellt, aber KI-Generierung ist nicht verfügbar. Bitte fügen Sie den Inhalt manuell hinzu.')
        except Exception as e:
            messages.warning(self.request, f'Dokument wurde erstellt, aber KI-Generierung fehlgeschlagen: {str(e)}. Bitte fügen Sie den Inhalt manuell hinzu.')
        
        return super().form_valid(form)


class DocumentUpdateView(UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'
    
    def get_success_url(self):
        return reverse_lazy('documents:document_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Dokument wurde erfolgreich aktualisiert.')

        # Handle HTMX requests
        if self.request.headers.get("HX-Request"):
            response = HttpResponse()
            response["HX-Redirect"] = self.get_success_url()
            return response

        return response


class DocumentDeleteView(DeleteView):
    model = Document
    template_name = 'documents/document_confirm_delete.html'
    success_url = reverse_lazy('documents:document_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Dokument wurde erfolgreich gelöscht.')

        # Handle HTMX requests
        if self.request.headers.get("HX-Request"):
            response = HttpResponse()
            response["HX-Redirect"] = self.get_success_url()
            return response

        return response


@method_decorator(csrf_exempt, name="dispatch")
class SaveDocumentContentView(View):
    """View for saving document content via AJAX"""
    
    def post(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        
        try:
            data = json.loads(request.body)
            content = data.get("content", "")
            
            document.content = content
            document.save()
            
            return JsonResponse({"success": True})
            
        except Exception as e:
            return JsonResponse({"error": f"Fehler beim Speichern: {str(e)}"}, status=400)


@method_decorator(csrf_exempt, name="dispatch")
class GenerateDocumentView(View):
    """View for generating documents using AI"""
    
    def post(self, request, patient_pk, therapy_pk):
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
                document_type=document_type
            )
            
            return JsonResponse({
                "success": True, 
                "document_id": document.pk,
                "content": generated_content
            })
            
        except Exception as e:
            return JsonResponse({"error": f"Fehler bei der Dokumentgenerierung: {str(e)}"}, status=400)


class DocumentFormView(View):
    """View for displaying document generation form"""
    
    def get(self, request, patient_pk, therapy_pk):
        patient = get_object_or_404(Patient, pk=patient_pk)
        therapy = get_object_or_404(Therapy, pk=therapy_pk, patient=patient)
        
        context = {
            'patient': patient,
            'therapy': therapy,
            'document_types': get_available_document_types(),
        }
        
        return render(request, 'documents/document_form.html', context)
