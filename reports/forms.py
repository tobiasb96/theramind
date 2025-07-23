from django import forms
from django.utils import timezone
from document_templates.models import DocumentTemplate
from .models import Report
from users.mixins import UserFormMixin


class ReportForm(UserFormMixin, forms.ModelForm):
    template = forms.ModelChoiceField(
        queryset=DocumentTemplate.objects.none(),
        required=False,
        empty_label="Standard Template verwenden",
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Template",
    )

    class Meta:
        model = Report
        fields = ["title", "patient_gender", "template"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "z.B. Erstgespräch Bericht"}
            ),
            "patient_gender": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make title field optional but provide helpful text
        self.fields["title"].required = False
        self.fields[
            "title"
        ].help_text = "Optional - wenn leer, wird automatisch 'Bericht vom [Datum]' verwendet"

        if hasattr(self, 'user') and self.user:
            from django.db.models import Q
            self.fields["template"].queryset = DocumentTemplate.objects.filter(
                template_type=DocumentTemplate.TemplateType.REPORT, 
                is_active=True
            ).filter(
                Q(is_predefined=True) | Q(user=self.user)
            ).order_by("is_predefined", "name")
        else:
            # Fallback: show only predefined templates if no user context
            self.fields["template"].queryset = DocumentTemplate.objects.filter(
                template_type=DocumentTemplate.TemplateType.REPORT, 
                is_active=True,
                is_predefined=True
            ).order_by("name")

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Set default title if empty
        if not instance.title:
            instance.title = f"Bericht vom {timezone.now().strftime('%d.%m.%Y')}"

        if commit:
            instance.save()

        return instance


class ReportContentForm(forms.ModelForm):
    """Form for editing report content"""
    
    class Meta:
        model = Report
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 20
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].label = "Berichtinhalt"
