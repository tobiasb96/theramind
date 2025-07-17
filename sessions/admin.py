from django.contrib import admin
from .models import Session, AudioRecording, Transcription


class SessionInline(admin.TabularInline):
    model = Session
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class AudioRecordingInline(admin.TabularInline):
    model = AudioRecording
    extra = 0
    readonly_fields = ["filename", "file_size", "is_processed", "created_at"]


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ["therapy", "date", "duration", "title", "created_at"]
    list_filter = ["date", "therapy__patient", "created_at"]
    search_fields = [
        "therapy__patient__first_name",
        "therapy__patient__last_name",
        "title",
        "notes",
    ]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [AudioRecordingInline]
    fieldsets = (
        ("Therapie", {"fields": ("therapy",)}),
        ("Sitzungsdetails", {"fields": ("date", "duration", "title")}),
        ("Inhalt", {"fields": ("notes", "summary")}),
        ("System", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(AudioRecording)
class AudioRecordingAdmin(admin.ModelAdmin):
    list_display = ['session', 'filename', 'file_size', 'is_processed', 'created_at']
    list_filter = ['is_processed', 'created_at']
    search_fields = ['session__therapy__patient__first_name', 'session__therapy__patient__last_name', 'filename']
    readonly_fields = ['filename', 'file_size', 'created_at']


@admin.register(Transcription)
class TranscriptionAdmin(admin.ModelAdmin):
    list_display = ['recording', 'language', 'confidence', 'processing_time_seconds', 'created_at']
    list_filter = ['language', 'created_at']
    search_fields = ['recording__session__therapy__patient__first_name', 'recording__session__therapy__patient__last_name', 'text']
    readonly_fields = ['created_at']
