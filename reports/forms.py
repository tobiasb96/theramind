from django import forms
from document_templates.models import DocumentTemplate
from .models import Report, ReportContextFile
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
        fields = ["title", "template"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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


class ReportContextFileForm(forms.ModelForm):
    """Form for uploading context files"""
    
    class Meta:
        model = ReportContextFile
        fields = ["original_file"]
        widgets = {
            "original_file": forms.FileInput(attrs={
                "class": "form-control",
                "accept": ".pdf,.docx,.doc,.txt",
                "multiple": False
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["original_file"].label = "Datei hochladen"
        self.fields["original_file"].help_text = "Unterstützte Formate: PDF, Word (.docx, .doc), Text (.txt)"


class ReportContextTextForm(forms.ModelForm):
    """Form for manual text input as context"""
    
    text_input = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 10,
            "placeholder": "Geben Sie hier den Text ein, der als Kontext für den Bericht verwendet werden soll..."
        }),
        label="Text eingeben",
        help_text="Geben Sie den Text direkt ein, der als Kontext für die Berichtgenerierung verwendet werden soll."
    )
    
    class Meta:
        model = ReportContextFile
        fields = ["file_name"]
        widgets = {
            "file_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "z.B. Notizen vom 15.01.2024"
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file_name"].label = "Bezeichnung"
        self.fields["file_name"].help_text = "Geben Sie eine aussagekräftige Bezeichnung für diesen Text ein"
        
        # Set default file name if not provided
        if not self.instance.pk and not self.initial.get("file_name"):
            from django.utils import timezone
            self.initial["file_name"] = f"Manueller Text vom {timezone.now().strftime('%d.%m.%Y')}"


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
