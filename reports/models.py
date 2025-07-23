from django.db import models
from django.core.files.storage import default_storage
from django.conf import settings
from core.models import BaseDocument


class Report(BaseDocument):
    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

    @property
    def has_context(self):
        """Check if report has any context files"""
        return self.context_files.exists()

    @property
    def context_files_count(self):
        """Get count of context files"""
        return self.context_files.count()
