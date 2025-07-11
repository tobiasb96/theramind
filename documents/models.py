from django.db import models
from django.utils import timezone
from core.models import Patient
from therapy.models import Therapy, Session


class Document(models.Model):
    DOCUMENT_TYPES = [
        ('abschlussbericht', 'Abschlussbericht'),
        ('verlaufsbericht', 'Verlaufsbericht'),
        ('befundbericht', 'Befundbericht'),
        ('indikationsstellung', 'Indikationsstellung'),
        ('anamnese', 'Anamnese'),
        ('diagnose', 'Diagnose'),
        ('therapieplan', 'Therapieplan'),
        ('brief', 'Brief'),
        ('other', 'Sonstiges'),
    ]
    
    therapy = models.ForeignKey(Therapy, on_delete=models.CASCADE, verbose_name="Therapie")
    title = models.CharField(max_length=200, verbose_name="Titel")
    content = models.TextField(verbose_name="Inhalt")
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='abschlussbericht', verbose_name="Dokumenttyp")
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
