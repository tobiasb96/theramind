from django.db import models
from django.utils import timezone
from core.models import Patient


class Therapy(models.Model):
    STATUS_CHOICES = [
        ('active', 'Aktiv'),
        ('completed', 'Abgeschlossen'),
        ('paused', 'Pausiert'),
        ('cancelled', 'Abgebrochen'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Patient")
    title = models.CharField(max_length=200, verbose_name="Titel")
    description = models.TextField(verbose_name="Beschreibung", blank=True)
    start_date = models.DateField(default=timezone.now, verbose_name="Startdatum")
    end_date = models.DateField(null=True, blank=True, verbose_name="Enddatum")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    goals = models.TextField(verbose_name="Therapieziele", blank=True)
    notes = models.TextField(verbose_name="Notizen", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")
    
    class Meta:
        verbose_name = "Therapie"
        verbose_name_plural = "Therapien"
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.title}"
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def session_count(self):
        return self.session_set.count()


class Session(models.Model):
    therapy = models.ForeignKey(Therapy, on_delete=models.CASCADE, verbose_name="Therapie")
    date = models.DateTimeField(default=timezone.now, verbose_name="Datum")
    duration = models.PositiveIntegerField(verbose_name="Dauer (Minuten)")
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
        return f"{self.therapy.patient.full_name} - {self.date.strftime('%d.%m.%Y %H:%M')}"
    
    @property
    def patient(self):
        return self.therapy.patient


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
