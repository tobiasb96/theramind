from django import forms
from .models import Report, ReportTemplate
from sessions.models import Session


class ReportForm(forms.ModelForm):
    template = forms.ModelChoiceField(
        queryset=ReportTemplate.objects.none(),
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
        self.fields["template"].queryset = ReportTemplate.objects.filter(
            template_type=ReportTemplate.TemplateType.REPORT, is_active=True
        ).order_by("is_predefined", "name")
