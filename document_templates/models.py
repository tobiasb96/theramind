from django.db import models
from django.conf import settings


class DocumentTemplate(models.Model):
    """Custom report templates for users"""

    class TemplateType(models.TextChoices):
        REPORT = "report", "Bericht"
        SESSION_NOTES = "session_notes", "Sitzungsnotiz"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name="Benutzer",
        null=True,
        blank=True
    )

    name = models.CharField(max_length=200, verbose_name="Template Name")
    description = models.TextField(verbose_name="Beschreibung", blank=True)
    template_type = models.CharField(
        max_length=20, choices=TemplateType.choices, verbose_name="Template Typ"
    )

    # Template content
    system_prompt = models.TextField(
        verbose_name="System Prompt",
        help_text="Der System-Prompt für die KI-Generierung",
        blank=True,
    )
    user_prompt = models.TextField(
        verbose_name="User Prompt Template",
        help_text="Das Prompt-Template mit Platzhaltern wie {session_info}, etc.",
    )

    # Template settings
    max_tokens = models.PositiveIntegerField(default=2000, verbose_name="Max Tokens")
    temperature = models.FloatField(default=0.3, verbose_name="Temperature")

    # Metadata
    is_predefined = models.BooleanField(
        default=False,
        verbose_name="Vordefiniert",
        help_text="Ist dies ein vordefiniertes System-Template?",
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktiv")
    based_on_template = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Basiert auf Template",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")

    class Meta:
        verbose_name = "Dokument Template"
        verbose_name_plural = "Dokument Templates"
        ordering = ["name"]
        # Ensure unique template names per user (predefined templates have user=None)
        unique_together = [['user', 'name', 'template_type']]

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"

    @property
    def is_custom(self):
        return not self.is_predefined


class UserTemplatePreference(models.Model):
    """User preferences for default templates"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name="Benutzer",
        null=True,
        blank=True
    )

    # Default templates for document types
    default_document_templates = models.JSONField(
        default=dict,
        verbose_name="Standard Dokument Templates",
        help_text="Mapping von Dokumenttyp zu Template-ID",
    )

    # Default templates for session notes
    default_session_templates = models.JSONField(
        default=dict,
        verbose_name="Standard Sitzungsnotizen Templates",
        help_text="Mapping von Sitzungstyp zu Template-ID",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Benutzer Template Einstellungen"
        verbose_name_plural = "Benutzer Template Einstellungen"

    def __str__(self):
        return f"Template Einstellungen für {self.user}"
