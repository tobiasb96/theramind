from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["title", "input_count", "created_at", "updated_at"]
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'content']
    readonly_fields = ["created_at", "updated_at", "input_count"]
    
    fieldsets = (
        ("Grundinformationen", {"fields": ("title", "content", "patient_gender")}),
        (
            "Eingaben",
            {
                "fields": ("input_count",),
                "description": "Audio- und Dokumenteingaben über die Unified Input Service",
            },
        ),
        ("Metadaten", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def input_count(self, obj):
        """Display count of all inputs"""
        return obj.all_inputs["total_count"]

    input_count.short_description = "Anzahl Eingaben"
