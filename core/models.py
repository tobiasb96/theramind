from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.files.storage import default_storage


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

    # Export tracking
    is_exported = models.BooleanField(
        default=False,
        verbose_name="Exportiert",
        help_text="Gibt an, ob das Dokument bereits als Datei exportiert wurde",
    )

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

    @property
    def audio_inputs(self):
        """Get all audio inputs for this document"""
        return AudioInput.objects.filter(
            content_type=ContentType.objects.get_for_model(self), object_id=self.pk
        )

    @property
    def document_inputs(self):
        """Get all document inputs for this document"""
        return DocumentInput.objects.filter(
            content_type=ContentType.objects.get_for_model(self), object_id=self.pk
        )

    @property
    def all_inputs(self):
        """Get combined count of all inputs"""
        return {
            "audio_count": self.audio_inputs.count(),
            "document_count": self.document_inputs.count(),
            "total_count": self.audio_inputs.count() + self.document_inputs.count(),
        }

    def mark_as_exported(self):
        """Mark the document as exported"""
        self.is_exported = True
        self.save()


class BaseInput(models.Model):
    """
    Abstract base model for all document inputs (audio and documents)
    """

    # Generic foreign key to BaseDocument (Session or Report)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    document = GenericForeignKey("content_type", "object_id")

    # Common metadata
    name = models.CharField(max_length=255, verbose_name="Name")
    description = models.TextField(blank=True, verbose_name="Beschreibung")

    # Processing status
    processing_successful = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def mark_as_failed(self, error_message: str):
        """Mark the input as failed and set the error message"""
        self.processing_successful = False
        self.processing_error = error_message
        self.save()

    def mark_as_successful(self):
        """Mark the input as successful"""
        self.processing_successful = True
        self.processing_error = ""
        self.save()


class AudioInput(BaseInput):
    """
    Model for audio inputs (recordings and uploads) for both Sessions and Reports
    """

    class AudioType(models.TextChoices):
        RECORDING = "recording", "Aufnahme"
        UPLOAD = "upload", "Upload"

    class FileFormat(models.TextChoices):
        MP3 = "mp3", "MP3"
        WAV = "wav", "WAV"
        M4A = "m4a", "M4A"
        WEBM = "webm", "WebM"
        FLAC = "flac", "FLAC"

    # Audio-specific fields
    audio_type = models.CharField(max_length=20, choices=AudioType.choices)
    file_format = models.CharField(max_length=10, choices=FileFormat.choices, null=True, blank=True)

    # File storage
    audio_file = models.FileField(upload_to="audio_inputs/%Y/%m/%d/")
    file_size = models.PositiveIntegerField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)

    # Transcription
    transcribed_text = models.TextField(blank=True, verbose_name="Transkript")
    transcription_confidence = models.FloatField(null=True, blank=True)
    processing_time_seconds = models.FloatField(null=True, blank=True)
    language = models.CharField(max_length=10, default="de")

    class Meta:
        verbose_name = "Audio-Eingabe"
        verbose_name_plural = "Audio-Eingaben"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_audio_type_display()})"

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
        if self.audio_file:
            if default_storage.exists(self.audio_file.name):
                default_storage.delete(self.audio_file.name)
        super().delete(*args, **kwargs)

    def add_transcription(self, transcribed_text: str, processing_time: float):
        """Mark the input as successful and add the transcription"""
        self.transcribed_text = transcribed_text
        self.processing_time_seconds = processing_time
        self.save()


class DocumentInput(BaseInput):
    """
    Model for document and text inputs for both Sessions and Reports
    """

    class InputType(models.TextChoices):
        FILE_UPLOAD = "file", "Datei-Upload"
        MANUAL_TEXT = "text", "Manueller Text"

    class FileType(models.TextChoices):
        PDF = "pdf", "PDF"
        WORD = "word", "Word Document"
        TXT = "txt", "Text File"
        MANUAL = "manual", "Eigener Text"

    # Document-specific fields
    input_type = models.CharField(max_length=20, choices=InputType.choices)
    file_type = models.CharField(max_length=20, choices=FileType.choices, null=True, blank=True)

    # File storage (only for file uploads)
    document_file = models.FileField(upload_to="document_inputs/%Y/%m/%d/", null=True, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)

    # Extracted/manual content
    extracted_text = models.TextField(verbose_name="Text-Inhalt")

    class Meta:
        verbose_name = "Dokument-Eingabe"
        verbose_name_plural = "Dokument-Eingaben"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_input_type_display()})"

    def get_text_preview(self, max_length=100):
        """Get a preview of the text content"""
        if not self.extracted_text:
            return "Kein Text verfügbar"

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
        if self.document_file:
            if default_storage.exists(self.document_file.name):
                default_storage.delete(self.document_file.name)
        super().delete(*args, **kwargs)
