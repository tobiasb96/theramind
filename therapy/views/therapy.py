from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from rest_framework import viewsets

from patients.models import Patient
from therapy.models import Therapy
from therapy.forms import TherapyForm


class TherapyViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing therapy CRUD operations.
    """
    
    def get_queryset(self):
        return Therapy.objects.all().order_by('-start_date')
    
    def list(self, request, patient_pk=None):
        """List all therapies"""
        therapies = self.get_queryset()
        
        # Handle pagination
        paginator = Paginator(therapies, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'therapy/session_list.html', {
            'therapies': page_obj,
            'page_obj': page_obj,
        })
    
    def retrieve(self, request, patient_pk=None, pk=None):
        """Retrieve a specific therapy"""
        therapy = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Get related sessions and documents
        sessions = therapy.session_set.order_by('-date')
        documents = therapy.document_set.order_by('-created_at')
        
        return render(request, 'therapy/session_detail.html', {
            'therapy': therapy,
            'sessions': sessions,
            'documents': documents,
        })
    
    def create(self, request, patient_pk=None):
        """Create a new therapy"""
        if request.method == 'GET':
            form = TherapyForm()
            
            # Pre-populate patient if provided
            patient_id = request.GET.get('patient')
            if patient_id:
                try:
                    patient = Patient.objects.get(pk=patient_id)
                    form.initial['patient'] = patient
                except Patient.DoesNotExist:
                    pass
            
            return render(request, 'therapy/session_form.html', {'form': form})
        
        elif request.method == 'POST':
            form = TherapyForm(request.POST)
            if form.is_valid():
                therapy = form.save()
                messages.success(request, 'Therapie wurde erfolgreich angelegt.')
                return HttpResponseRedirect(reverse_lazy('therapy:therapy_detail', kwargs={'pk': therapy.pk}))
            
            return render(request, 'therapy/session_form.html', {'form': form})
    
    def update(self, request, patient_pk=None, pk=None):
        """Update an existing therapy"""
        therapy = get_object_or_404(self.get_queryset(), pk=pk)
        
        if request.method == 'GET':
            form = TherapyForm(instance=therapy)
            return render(request, 'therapy/session_form.html', {'form': form, 'therapy': therapy})
        
        elif request.method == 'POST':
            form = TherapyForm(request.POST, instance=therapy)
            if form.is_valid():
                form.save()
                messages.success(request, 'Therapie wurde erfolgreich aktualisiert.')
                return HttpResponseRedirect(reverse_lazy('therapy:therapy_detail', kwargs={'pk': therapy.pk}))
            
            return render(request, 'therapy/session_form.html', {'form': form, 'therapy': therapy})
    
    def destroy(self, request, patient_pk=None, pk=None):
        """Delete a therapy"""
        therapy = get_object_or_404(self.get_queryset(), pk=pk)
        
        if request.method == 'GET':
            return render(request, 'therapy/session_confirm_delete.html', {'therapy': therapy})
        
        elif request.method == 'POST':
            therapy.delete()
            messages.success(request, 'Therapie wurde erfolgreich gelöscht.')
            return HttpResponseRedirect(reverse_lazy('therapy:therapy_list')) 