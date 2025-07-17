from django import forms
from document_templates.models import DocumentTemplate
from .models import Report
from therapy_sessions.models import Session


class ReportForm(forms.ModelForm):
    template = forms.ModelChoiceField(
        queryset=DocumentTemplate.objects.none(),
        required=False,
        empty_label="Standard Template verwenden",
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Template",
    )

    class Meta:
        model = Report
        fields = ["title", "sessions", "template"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "sessions": forms.SelectMultiple(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sessions"].queryset = Session.objects.order_by("-date")
        self.fields["template"].queryset = DocumentTemplate.objects.filter(
            template_type=DocumentTemplate.TemplateType.REPORT, is_active=True
        ).order_by("is_predefined", "name")
