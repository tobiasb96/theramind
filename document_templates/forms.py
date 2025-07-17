from django import forms
from .models import DocumentTemplate


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
