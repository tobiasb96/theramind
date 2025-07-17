from django.db import models
from sessions.models import Session


class Report(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titel")
    content = models.TextField(verbose_name="Inhalt")
    sessions = models.ManyToManyField(Session, blank=True, verbose_name="Zugehörige Sitzungen")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")
    
    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
