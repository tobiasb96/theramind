from django import forms
from .models import Patient, Settings


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'date_of_birth', 'email', 'phone', 'address', 'notes']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = [
            'transcript_ttl_hours',
            'openai_api_key',
            'max_audio_duration_minutes',
            'auto_transcribe',
            'auto_summarize'
        ]
        widgets = {
            'transcript_ttl_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'openai_api_key': forms.PasswordInput(attrs={'class': 'form-control'}),
            'max_audio_duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'auto_transcribe': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_summarize': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }