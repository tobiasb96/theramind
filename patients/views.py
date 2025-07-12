from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from rest_framework import viewsets
from rest_framework.decorators import action
from django_tables2 import RequestConfig

from .models import Patient, Settings
from .forms import PatientForm, SettingsForm
from .tables import PatientTable
from therapy.models import Session


class PatientViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing patient CRUD operations.
    """

    def get_queryset(self):
        return Patient.objects.annotate(session_count=Count("therapy__session")).order_by(
            "last_name", "first_name"
        )

    def list(self, request):
        """List all patients"""
        patients = self.get_queryset()

        # Handle search
        search_query = request.GET.get("search", "")
        if search_query:
            patients = patients.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(email__icontains=search_query)
            )

        # Create table with proper ordering
        table = PatientTable(patients)
        RequestConfig(request, paginate={"per_page": 20}).configure(table)

        return render(
            request,
            "patients/patient_list.html",
            {
                "table": table,
                "search_query": search_query,
                "form": PatientForm(),
            },
        )

    def retrieve(self, request, pk=None):
        """Retrieve a specific patient"""
        patient = get_object_or_404(Patient, pk=pk)

        # Get related data
        therapies = patient.therapy_set.order_by("-start_date")
        sessions = Session.objects.filter(therapy__patient=patient).order_by("-date")

        # Get all documents across all therapies for this patient
        from documents.models import Document
        from documents.prompts import get_available_document_types

        documents = Document.objects.filter(therapy__patient=patient).order_by("-created_at")

        return render(
            request,
            "patients/patient_detail.html",
            {
                "patient": patient,
                "therapies": therapies,
                "sessions": sessions,
                "documents": documents,
                "form": PatientForm(instance=patient),
                "document_types": get_available_document_types(),
            },
        )

    def create(self, request):
        """Create a new patient"""
        if request.method == "GET":
            form = PatientForm()
            return render(request, "patients/patient_form.html", {"form": form})

        elif request.method == "POST":
            form = PatientForm(request.POST)
            if form.is_valid():
                patient = form.save()
                messages.success(request, "Patient wurde erfolgreich angelegt.")

                # Handle HTMX requests
                if request.headers.get("HX-Request"):
                    response = HttpResponse()
                    response["HX-Redirect"] = reverse_lazy("patients:patient_list")
                    return response

                return HttpResponse(
                    status=302, headers={"Location": reverse_lazy("patients:patient_list")}
                )

            return render(request, "patients/patient_form.html", {"form": form})

    def update(self, request, pk=None):
        """Update an existing patient"""
        patient = get_object_or_404(Patient, pk=pk)

        if request.method == "GET":
            form = PatientForm(instance=patient)
            return render(request, "patients/patient_form.html", {"form": form, "patient": patient})

        elif request.method == "POST":
            form = PatientForm(request.POST, instance=patient)
            if form.is_valid():
                form.save()
                messages.success(request, "Patient wurde erfolgreich aktualisiert.")

                # Handle HTMX requests
                if request.headers.get("HX-Request"):
                    response = HttpResponse()
                    response["HX-Redirect"] = reverse_lazy(
                        "patients:patient_detail", kwargs={"pk": patient.pk}
                    )
                    return response

                return HttpResponse(
                    status=302,
                    headers={
                        "Location": reverse_lazy(
                            "patients:patient_detail", kwargs={"pk": patient.pk}
                        )
                    },
                )

            return render(request, "patients/patient_form.html", {"form": form, "patient": patient})

    def destroy(self, request, pk=None):
        """Delete a patient"""
        patient = get_object_or_404(Patient, pk=pk)

        if request.method == "GET":
            return render(request, "patients/patient_confirm_delete.html", {"patient": patient})

        elif request.method == "POST":
            patient.delete()
            messages.success(request, "Patient wurde erfolgreich gelöscht.")

            # Handle HTMX requests
            if request.headers.get("HX-Request"):
                response = HttpResponse()
                response["HX-Redirect"] = reverse_lazy("patients:patient_list")
                return response

            return HttpResponse(
                status=302, headers={"Location": reverse_lazy("patients:patient_list")}
            )


class SettingsView(UpdateView):
    model = Settings
    form_class = SettingsForm
    template_name = "patients/settings.html"
    success_url = reverse_lazy("patients:settings")

    def get_object(self):
        return Settings.get_settings()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["patient_count"] = Patient.objects.count()
        context["session_count"] = Session.objects.count()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # Reinitialize AI service after settings change
        from transcriptions.services import get_ai_service

        ai_service = get_ai_service()
        ai_service.reinitialize()
        messages.success(self.request, "Einstellungen wurden erfolgreich gespeichert.")
        return response
