from django import forms
from .models import Session, AudioRecording, Therapy
from patients.models import Patient


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
    # Optional patient selection field for quick creation
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.none(),
        required=False,
        empty_label="Patient auswählen",
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Patient",
    )

    class Meta:
        model = Session
        fields = ["patient", "therapy", "date", "duration", "title"]
        widgets = {
            "therapy": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "duration": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
        }
    
    def __init__(self, *args, **kwargs):
        # Extract patient_required parameter
        patient_required = kwargs.pop("patient_required", False)
        super().__init__(*args, **kwargs)

        # Set up patient field
        self.fields["patient"].queryset = Patient.objects.order_by("last_name", "first_name")
        self.fields["patient"].required = patient_required

        # Set up therapy field
        self.fields['therapy'].queryset = Therapy.objects.filter(status='active').order_by('-start_date')

        # If patient is not required, hide the patient field initially
        if not patient_required:
            self.fields["patient"].widget = forms.HiddenInput()


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