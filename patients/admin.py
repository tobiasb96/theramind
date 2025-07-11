from django.contrib import admin
from .models import Patient, Settings


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'email', 'phone', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['first_name', 'last_name', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Persönliche Daten', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'email', 'phone')
        }),
        ('Adresse', {
            'fields': ('address',)
        }),
        ('Notizen', {
            'fields': ('notes',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'auto_transcribe', 'auto_summarize', 'updated_at']
    fieldsets = (
        ('Transkription', {
            'fields': ('transcript_ttl_hours', 'auto_transcribe', 'max_audio_duration_minutes')
        }),
        ('KI-Einstellungen', {
            'fields': ('openai_api_key', 'auto_summarize')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        return not Settings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
