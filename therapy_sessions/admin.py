from django.contrib import admin
from .models import Session


class SessionInline(admin.TabularInline):
    model = Session
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ["date", "title", "created_at"]
    list_filter = ["date", "created_at"]
    search_fields = ["title", "content"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("Sitzungsdetails", {"fields": ("date", "title")}),
        ("Inhalt", {"fields": ("content", "summary")}),
        ("System", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
