from django import forms
from .models import Document, DocumentTemplate
from therapy.models import Therapy, Session
from .prompts import get_available_document_types


class DocumentForm(forms.ModelForm):
    template = forms.ModelChoiceField(
        queryset=DocumentTemplate.objects.none(),
        required=False,
        empty_label="Standard Template verwenden",
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Template",
    )

    class Meta:
        model = Document
        fields = ["therapy", "title", "document_type", "sessions", "template"]
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

        # Set up template choices
        self.fields["template"].queryset = DocumentTemplate.objects.filter(
            template_type="document", is_active=True
        ).order_by("is_predefined", "name")


class DocumentTemplateForm(forms.ModelForm):
    class Meta:
        model = DocumentTemplate
        fields = [
            "name",
            "description",
            "template_type",
            "document_type",
            "user_prompt",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "template_type": forms.Select(attrs={"class": "form-control"}),
            "document_type": forms.Select(attrs={"class": "form-control"}),
            "user_prompt": forms.Textarea(attrs={"class": "form-control", "rows": 15}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make document_type optional for session notes templates
        if self.instance and self.instance.template_type == "session_notes":
            self.fields["document_type"].required = False

        # Add help text
        self.fields[
            "user_prompt"
        ].help_text = "Das Template sollte nur die Struktur enthalten. Kontext-Variablen werden automatisch vom System hinzugefügt."
