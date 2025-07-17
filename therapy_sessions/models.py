from django.db import models
from django.utils import timezone
from django.conf import settings


class Session(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Benutzer", null=True, blank=True)
    date = models.DateTimeField(default=timezone.now, verbose_name="Datum")
    title = models.CharField(max_length=200, verbose_name="Titel", blank=True)
    notes = models.TextField(verbose_name="Notizen", blank=True)
    summary = models.TextField(verbose_name="Zusammenfassung", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")
    
    class Meta:
        verbose_name = "Sitzung"
        verbose_name_plural = "Sitzungen"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.title or 'Sitzung'} - {self.date.strftime('%d.%m.%Y %H:%M')}"


class AudioRecording(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, verbose_name="Sitzung")
    audio = models.FileField(upload_to="audio/%Y/%m/%d/", verbose_name="Audio-Datei")
    filename = models.CharField(max_length=255, verbose_name="Dateiname")
    file_size = models.PositiveIntegerField(verbose_name="Dateigröße (Bytes)", null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(verbose_name="Dauer (Sekunden)", null=True, blank=True)
    is_processed = models.BooleanField(default=False, verbose_name="Verarbeitet")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")
    
    class Meta:
        verbose_name = "Audio-Aufnahme"
        verbose_name_plural = "Audio-Aufnahmen"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.session} - {self.filename}"
    
    def save(self, *args, **kwargs):
        if self.audio and not self.filename:
            self.filename = self.audio.name
        super().save(*args, **kwargs)


class Transcription(models.Model):
    recording = models.OneToOneField(AudioRecording, on_delete=models.CASCADE, verbose_name="Aufnahme")
    text = models.TextField(verbose_name="Transkript")
    confidence = models.FloatField(null=True, blank=True, verbose_name="Genauigkeit")
    language = models.CharField(max_length=10, default="de", verbose_name="Sprache")
    processing_time_seconds = models.FloatField(null=True, blank=True, verbose_name="Verarbeitungszeit")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")
    
    class Meta:
        verbose_name = "Transkription"
        verbose_name_plural = "Transkriptionen"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transkript: {self.recording.session}"


class Settings(models.Model):
    transcript_ttl_hours = models.PositiveIntegerField(
        default=24,
        verbose_name="Transkript-Aufbewahrungszeit (Stunden)",
        help_text="Nach wie vielen Stunden werden Transkripte automatisch gelöscht?",
    )
    openai_api_key = models.CharField(
        max_length=255,
        verbose_name="OpenAI API Key",
        help_text="API Key für OpenAI Whisper und GPT",
        blank=True,
    )
    max_audio_duration_minutes = models.PositiveIntegerField(
        default=60,
        verbose_name="Maximale Audio-Dauer (Minuten)",
        help_text="Maximale Länge für Audio-Aufnahmen",
    )
    auto_transcribe = models.BooleanField(
        default=True,
        verbose_name="Automatische Transkription",
        help_text="Sollen Audio-Aufnahmen automatisch transkribiert werden?",
    )
    auto_summarize = models.BooleanField(
        default=True,
        verbose_name="Automatische Zusammenfassung",
        help_text="Sollen Transkripte automatisch zusammengefasst werden?",
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
