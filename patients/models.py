from django.db import models
from uuid import uuid4


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    first_name = models.CharField(max_length=100, verbose_name="Vorname")
    last_name = models.CharField(max_length=100, verbose_name="Nachname")
    date_of_birth = models.DateField(verbose_name="Geburtsdatum", null=True, blank=True)
    email = models.EmailField(verbose_name="E-Mail", null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name="Telefon", null=True, blank=True)
    address = models.TextField(verbose_name="Adresse", null=True, blank=True)
    notes = models.TextField(verbose_name="Notizen", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")
    
    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patienten"
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Settings(models.Model):
    transcript_ttl_hours = models.PositiveIntegerField(
        default=24,
        verbose_name="Transkript-Aufbewahrungszeit (Stunden)",
        help_text="Nach wie vielen Stunden werden Transkripte automatisch gelöscht?"
    )
    openai_api_key = models.CharField(
        max_length=255,
        verbose_name="OpenAI API Key",
        help_text="API Key für OpenAI Whisper und GPT",
        blank=True
    )
    max_audio_duration_minutes = models.PositiveIntegerField(
        default=60,
        verbose_name="Maximale Audio-Dauer (Minuten)",
        help_text="Maximale Länge für Audio-Aufnahmen"
    )
    auto_transcribe = models.BooleanField(
        default=True,
        verbose_name="Automatische Transkription",
        help_text="Sollen Audio-Aufnahmen automatisch transkribiert werden?"
    )
    auto_summarize = models.BooleanField(
        default=True,
        verbose_name="Automatische Zusammenfassung",
        help_text="Sollen Transkripte automatisch zusammengefasst werden?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Einstellungen"
        verbose_name_plural = "Einstellungen"
    
    def __str__(self):
        return "Anwendungseinstellungen"
    
    @classmethod
    def get_settings(cls):
        """Get or create singleton settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
