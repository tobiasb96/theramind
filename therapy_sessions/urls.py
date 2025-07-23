from django.urls import path
from .views import SessionViewSet

app_name = "sessions"

# Initialize ViewSets
session_viewset = SessionViewSet()

urlpatterns = [
    # Session URLs (now standalone)
    path("", session_viewset.list, name="session_list"),
    path("create/", session_viewset.create, name="session_create"),
    path("<int:pk>/", session_viewset.retrieve, name="session_detail"),
    path("<int:pk>/edit/", session_viewset.update, name="session_edit"),
    path("<int:pk>/delete/", session_viewset.destroy, name="session_delete"),
    path(
        "<int:pk>/save-transcript/",
        session_viewset.save_transcript,
        name="session_save_transcript",
    ),
    path(
        "<int:pk>/generate-notes/",
        session_viewset.generate_notes,
        name="session_generate_notes",
    ),
    path("<int:pk>/save-notes/", session_viewset.save_notes, name="session_save_notes"),
    path(
        "<int:pk>/create-from-template/",
        session_viewset.create_from_template,
        name="session_create_from_template",
    ),
    # Export and delete notes
    path(
        "<int:pk>/export-notes/pdf/",
        session_viewset.export_notes_pdf,
        name="session_export_notes_pdf",
    ),
    path(
        "<int:pk>/delete-notes/",
        session_viewset.delete_notes,
        name="session_delete_notes",
    ),
]