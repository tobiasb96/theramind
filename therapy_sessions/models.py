from django.db import models
from django.utils import timezone
from core.models import BaseDocument


class Session(BaseDocument):
    # Session-specific fields
    date = models.DateTimeField(default=timezone.now, verbose_name="Datum")

    # Map notes to content field in BaseDocument
    # We'll keep notes as a property for backward compatibility
    @property
    def notes(self):
        return self.content

    @notes.setter
    def notes(self, value):
        self.content = value
    
    class Meta:
        verbose_name = "Sitzung"
        verbose_name_plural = "Sitzungen"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.title or 'Sitzung'} - {self.date.strftime('%d.%m.%Y %H:%M')}"
