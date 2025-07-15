from django import forms
from .models import Document, DocumentTemplate
from therapy.models import Therapy, Session
from patients.models import Patient


class DocumentForm(forms.ModelForm):
    # Optional patient selection field for quick creation
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.none(),
        required=False,
        empty_label="Patient auswählen",
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Patient",
    )

    template = forms.ModelChoiceField(
        queryset=DocumentTemplate.objects.none(),
        required=False,
        empty_label="Standard Template verwenden",
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Template",
    )

    class Meta:
        model = Document
        fields = ["patient", "therapy", "title", "sessions", "template"]
        widgets = {
            "therapy": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "sessions": forms.SelectMultiple(attrs={"class": "form-control"}),
        }
    
    def __init__(self, *args, **kwargs):
        # Extract patient_required parameter
        patient_required = kwargs.pop("patient_required", False)
        super().__init__(*args, **kwargs)

        # Set up patient field
        self.fields["patient"].queryset = Patient.objects.order_by("last_name", "first_name")
        self.fields["patient"].required = patient_required

        # Set up other fields
        self.fields['therapy'].queryset = Therapy.objects.order_by('-start_date')
        self.fields['sessions'].queryset = Session.objects.select_related('therapy__patient').order_by('-date')

        # Set up template choices
        self.fields["template"].queryset = DocumentTemplate.objects.filter(
            template_type="document", is_active=True
        ).order_by("is_predefined", "name")

        # If patient is not required, hide the patient field initially
        if not patient_required:
            self.fields["patient"].widget = forms.HiddenInput()


class DocumentTemplateForm(forms.ModelForm):
    class Meta:
        model = DocumentTemplate
        fields = [
            "name",
            "description",
            "template_type",
            "user_prompt",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "template_type": forms.Select(attrs={"class": "form-control"}),
            "user_prompt": forms.Textarea(attrs={"class": "form-control", "rows": 15}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add help text
        self.fields[
            "user_prompt"
        ].help_text = "Das Template sollte nur die Struktur enthalten. Kontext-Variablen werden automatisch vom System hinzugefügt."
