from django.db import models
from django.core.files.storage import default_storage
from django.conf import settings


class Report(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Benutzer", null=True, blank=True)
    title = models.CharField(max_length=200, verbose_name="Titel")
    content = models.TextField(verbose_name="Inhalt", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")
    
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


class ReportContextFile(models.Model):
    """Model for storing context files and their extracted text"""
    
    class FileType(models.TextChoices):
        PDF = 'pdf', 'PDF'
        WORD = 'word', 'Word Document'
        TXT = 'txt', 'Text File'
        MANUAL = "manual", "Eigener Text"
    
    report = models.ForeignKey(
        Report, 
        on_delete=models.CASCADE, 
        related_name='context_files',
        verbose_name="Bericht"
    )
    
    # File information
    file_name = models.CharField(max_length=255, verbose_name="Dateiname")
    file_type = models.CharField(
        max_length=20, 
        choices=FileType.choices, 
        verbose_name="Dateityp"
    )
    file_size = models.PositiveIntegerField(
        verbose_name="Dateigröße (Bytes)", 
        null=True, 
        blank=True
    )
    original_file = models.FileField(
        upload_to="report_context/%Y/%m/%d/", 
        verbose_name="Originaldatei",
        null=True,
        blank=True
    )
    
    # Extracted content
    extracted_text = models.TextField(verbose_name="Extrahierter Text")
    extraction_successful = models.BooleanField(
        default=False, 
        verbose_name="Extraktion erfolgreich"
    )
    extraction_error = models.TextField(
        verbose_name="Extraktionsfehler", 
        blank=True
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")
    
    class Meta:
        verbose_name = "Kontext-Datei"
        verbose_name_plural = "Kontext-Dateien"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.file_name} ({self.get_file_type_display()})"
    
    def get_text_preview(self, max_length=100):
        """Get a preview of the extracted text"""
        if not self.extracted_text:
            return "Kein Text extrahiert"
        
        if len(self.extracted_text) <= max_length:
            return self.extracted_text
        
        return self.extracted_text[:max_length] + "..."
    
    def get_file_size_display(self):
        """Get human-readable file size"""
        if not self.file_size:
            return "Unbekannt"
        
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size // 1024} KB"
        else:
            return f"{self.file_size // (1024 * 1024)} MB"
    
    def delete(self, *args, **kwargs):
        """Override delete to also remove the file from storage"""
        if self.original_file:
            if default_storage.exists(self.original_file.name):
                default_storage.delete(self.original_file.name)
        super().delete(*args, **kwargs)
