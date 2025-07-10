from django import forms
from .models import Session, AudioRecording, Therapy, Document
from core.models import Patient


class TherapyForm(forms.ModelForm):
    class Meta:
        model = Therapy
        fields = ['patient', 'title', 'description', 'start_date', 'end_date', 'status', 'goals', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'goals': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = Patient.objects.order_by('last_name', 'first_name')


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['therapy', 'date', 'duration', 'title', 'notes']
        widgets = {
            'therapy': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['therapy'].queryset = Therapy.objects.filter(status='active').order_by('-start_date')


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['therapy', 'title', 'content', 'document_type', 'sessions']
        widgets = {
            'therapy': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 12}),
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'sessions': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['therapy'].queryset = Therapy.objects.order_by('-start_date')
        self.fields['sessions'].queryset = Session.objects.select_related('therapy__patient').order_by('-date')


class AudioUploadForm(forms.ModelForm):
    class Meta:
        model = AudioRecording
        fields = ['audio']
        widgets = {
            'audio': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'audio/*'
            })
        }