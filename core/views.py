from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count
from django.http import HttpResponse
from .models import Patient, Settings
from .forms import PatientForm, SettingsForm
from therapy.models import Session


class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient_count'] = Patient.objects.count()
        context['session_count'] = Session.objects.count()

        # Get recent documents instead of sessions
        from documents.models import Document

        context["recent_documents"] = Document.objects.select_related("therapy__patient").order_by(
            "-created_at"
        )[:5]
        context['recent_patients'] = Patient.objects.order_by('-created_at')[:5]
        return context


class PatientListView(ListView):
    model = Patient
    template_name = 'core/patient_list.html'
    context_object_name = 'patients'
    paginate_by = 20
    
    def get_queryset(self):
        return Patient.objects.annotate(session_count=Count('therapy__session')).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PatientForm()
        return context


class PatientDetailView(DetailView):
    model = Patient
    template_name = 'core/patient_detail.html'
    context_object_name = 'patient'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['therapies'] = self.object.therapy_set.order_by('-start_date')
        # Get all sessions across all therapies for this patient
        context['sessions'] = Session.objects.filter(therapy__patient=self.object).order_by('-date')
        # Get all documents across all therapies for this patient
        from documents.models import Document
        from documents.prompts import get_available_document_types

        context["documents"] = Document.objects.filter(therapy__patient=self.object).order_by(
            "-created_at"
        )
        context["form"] = PatientForm(instance=self.object)
        context["document_types"] = get_available_document_types()
        return context


class PatientCreateView(CreateView):
    model = Patient
    form_class = PatientForm
    template_name = 'core/patient_form.html'
    success_url = reverse_lazy('core:patient_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Patient wurde erfolgreich angelegt.')

        # Handle HTMX requests
        if self.request.headers.get("HX-Request"):
            response = HttpResponse()
            response["HX-Redirect"] = self.get_success_url()
            return response

        return response


class PatientUpdateView(UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'core/patient_form.html'
    
    def get_success_url(self):
        return reverse_lazy('core:patient_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Patient wurde erfolgreich aktualisiert.')

        # Handle HTMX requests
        if self.request.headers.get("HX-Request"):
            response = HttpResponse()
            response["HX-Redirect"] = self.get_success_url()
            return response

        return response


class PatientDeleteView(DeleteView):
    model = Patient
    template_name = 'core/patient_confirm_delete.html'
    success_url = reverse_lazy('core:patient_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Patient wurde erfolgreich gelöscht.')

        # Handle HTMX requests
        if self.request.headers.get("HX-Request"):
            response = HttpResponse()
            response["HX-Redirect"] = self.get_success_url()
            return response

        return response


class SettingsView(UpdateView):
    model = Settings
    form_class = SettingsForm
    template_name = 'core/settings.html'
    success_url = reverse_lazy('core:settings')
    
    def get_object(self):
        return Settings.get_settings()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient_count'] = Patient.objects.count()
        context['session_count'] = Session.objects.count()
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Reinitialize AI service after settings change
        from ai.services import get_ai_service
        ai_service = get_ai_service()
        ai_service.reinitialize()
        messages.success(self.request, 'Einstellungen wurden erfolgreich gespeichert.')
        return response
