from django.db import models
from django.conf import settings


class BaseDocument(models.Model):
    """
    Abstract base model for documents like Sessions and Reports.
    Contains common fields that are shared across different document types.
    """
    
    class PatientGender(models.TextChoices):
        MALE = "male", "Männlich"
        FEMALE = "female", "Weiblich"
        DIVERSE = "diverse", "Divers"
        NOT_SPECIFIED = "not_specified", "Nicht angegeben"

    # User relationship
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="User",
        null=True,
        blank=True,
    )
    
    # Core document fields
    title = models.CharField(max_length=200, verbose_name="Titel", blank=True)
    content = models.TextField(verbose_name="Inhalt", blank=True)
    summary = models.TextField(verbose_name="Zusammenfassung", blank=True)
    
    # Patient information
    patient_gender = models.CharField(
        max_length=20,
        choices=PatientGender.choices,
        default=PatientGender.NOT_SPECIFIED,
        verbose_name="Geschlecht des Patienten",
        help_text="Geschlecht des Patienten für geschlechtsspezifische KI-Generierung",
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title or f"{self.__class__.__name__} #{self.pk}" 