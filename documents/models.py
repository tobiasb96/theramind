from django.db import models
from django.utils import timezone
from patients.models import Patient
from therapy.models import Therapy, Session


class Document(models.Model):
    therapy = models.ForeignKey(Therapy, on_delete=models.CASCADE, verbose_name="Therapie")
    title = models.CharField(max_length=200, verbose_name="Titel")
    content = models.TextField(verbose_name="Inhalt")
    sessions = models.ManyToManyField(Session, blank=True, verbose_name="Zugehörige Sitzungen")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")
    
    class Meta:
        verbose_name = "Dokument"
        verbose_name_plural = "Dokumente"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.therapy.patient.full_name} - {self.title}"
    
    @property
    def patient(self):
        return self.therapy.patient


class DocumentTemplate(models.Model):
    """Custom document templates for users"""

    TEMPLATE_TYPES = [
        ("document", "Dokumente"),
        ("session_notes", "Sitzungsnotizen"),
    ]

    # TODO: Add user reference when user model is implemented
    # user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Benutzer")

    name = models.CharField(max_length=200, verbose_name="Template Name")
    description = models.TextField(verbose_name="Beschreibung", blank=True)
    template_type = models.CharField(
        max_length=20, choices=TEMPLATE_TYPES, verbose_name="Template Typ"
    )

    # Template content
    system_prompt = models.TextField(
        verbose_name="System Prompt",
        help_text="Der System-Prompt für die KI-Generierung",
        blank=True,
    )
    user_prompt = models.TextField(
        verbose_name="User Prompt Template",
        help_text="Das Prompt-Template mit Platzhaltern wie {patient_info}, {therapy_info}, etc.",
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
        # TODO: Add unique constraint with user when user model is implemented
        # unique_together = [['user', 'name', 'template_type']]

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"

    @property
    def is_custom(self):
        return not self.is_predefined


class UserTemplatePreference(models.Model):
    """User preferences for default templates"""

    # TODO: Add user reference when user model is implemented
    # user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Benutzer")

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
        # TODO: Update when user model is implemented
        return f"Template Einstellungen für Benutzer"
