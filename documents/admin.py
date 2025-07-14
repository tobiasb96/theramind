from django.contrib import admin
from .models import Document, DocumentTemplate, UserTemplatePreference


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'therapy', 'document_type', 'created_at']
    list_filter = ["document_type", "created_at"]
    search_fields = ["title", "therapy__patient__first_name", "therapy__patient__last_name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "template_type",
        "document_type",
        "is_predefined",
        "is_active",
        "created_at",
    ]
    list_filter = ["template_type", "document_type", "is_predefined", "is_active"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        (
            "Grundinformationen",
            {"fields": ("name", "description", "template_type", "document_type")},
        ),
        (
            "Template Inhalt",
            {
                "fields": ("user_prompt",),
                "description": "System Prompt wird automatisch vom Code gesetzt",
            },
        ),
        ("Einstellungen", {"fields": ("max_tokens", "temperature", "is_active")}),
        (
            "Metadaten",
            {
                "fields": ("is_predefined", "based_on_template", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(UserTemplatePreference)
class UserTemplatePreferenceAdmin(admin.ModelAdmin):
    list_display = ["__str__", "created_at"]
    readonly_fields = ['created_at', 'updated_at']
