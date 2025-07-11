from django import forms
from .models import Document
from therapy.models import Therapy, Session
from .prompts import get_available_document_types


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['therapy', 'title', 'document_type', 'sessions']
        widgets = {
            'therapy': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'sessions': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['therapy'].queryset = Therapy.objects.order_by('-start_date')
        self.fields['sessions'].queryset = Session.objects.select_related('therapy__patient').order_by('-date')
        
        # Update document type choices to match available prompts
        document_types = get_available_document_types()
        self.fields['document_type'].choices = [('', 'Dokumenttyp auswählen')] + list(document_types.items()) 