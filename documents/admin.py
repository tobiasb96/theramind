from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'therapy', 'document_type', 'created_at']
    list_filter = ['document_type', 'created_at', 'therapy__patient']
    search_fields = ['title', 'content', 'therapy__patient__first_name', 'therapy__patient__last_name']
    date_hierarchy = 'created_at'
    filter_horizontal = ['sessions']
    
    fieldsets = (
        ('Grundinformationen', {
            'fields': ('therapy', 'title', 'document_type')
        }),
        ('Inhalt', {
            'fields': ('content',)
        }),
        ('Zugehörige Sitzungen', {
            'fields': ('sessions',),
            'classes': ('collapse',)
        }),
        ('Metadaten', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
