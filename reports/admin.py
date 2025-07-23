from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'context_files_count', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'content']
    readonly_fields = ["created_at", "updated_at", "context_files_count"]
    
    fieldsets = (
        ('Grundinformationen', {
            'fields': ('title', 'content')
        }),
        ('Kontext', {
            'fields': ('context_files_count',),
            'description': 'Kontextdateien werden in der Inline-Tabelle unten angezeigt'
        }),
        ('Metadaten', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def context_files_count(self, obj):
        """Display count of context files"""
        return obj.context_files_count
    context_files_count.short_description = 'Anzahl Kontextdateien'
