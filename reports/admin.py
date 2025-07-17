from django.contrib import admin
from .models import Report, ReportContextFile


class ReportContextFileInline(admin.TabularInline):
    """Inline admin for context files"""
    model = ReportContextFile
    extra = 0
    readonly_fields = ['file_size', 'file_type', 'extraction_successful', 'extraction_error', 'created_at']
    fields = ['file_name', 'file_type', 'original_file', 'file_size', 'extraction_successful', 'extraction_error', 'created_at']
    
    def has_add_permission(self, request, obj=None):
        return False  # Don't allow adding through admin


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'context_files_count', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at', 'context_files_count']
    inlines = [ReportContextFileInline]
    
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


@admin.register(ReportContextFile)
class ReportContextFileAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'file_type', 'report', 'extraction_successful', 'file_size', 'created_at']
    list_filter = ['file_type', 'extraction_successful', 'created_at']
    search_fields = ['file_name', 'report__title']
    readonly_fields = ['file_size', 'extraction_successful', 'extraction_error', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Dateiinformationen', {
            'fields': ('report', 'file_name', 'file_type', 'original_file', 'file_size')
        }),
        ('Textextraktion', {
            'fields': ('extraction_successful', 'extraction_error', 'extracted_text')
        }),
        ('Metadaten', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('report')
    
    def has_add_permission(self, request):
        return False  # Don't allow adding through admin, only through report interface
