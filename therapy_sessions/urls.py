from django.urls import path
from .views import SessionViewSet, AudioViewSet

app_name = "sessions"

# Initialize ViewSets
session_viewset = SessionViewSet()
audio_viewset = AudioViewSet()

urlpatterns = [
    # Session URLs (now standalone)
    path("sessions/", session_viewset.list, name="session_list"),
    path("sessions/create/", session_viewset.create, name="session_create"),
    path("sessions/<int:pk>/", session_viewset.retrieve, name="session_detail"),
    path("sessions/<int:pk>/edit/", session_viewset.update, name="session_edit"),
    path("sessions/<int:pk>/delete/", session_viewset.destroy, name="session_delete"),
    # Session custom actions
    path("sessions/<int:pk>/upload-audio/", audio_viewset.upload, name="session_audio_upload"),
    path(
        "sessions/<int:pk>/save-transcript/",
        session_viewset.save_transcript,
        name="session_save_transcript",
    ),
    path(
        "sessions/<int:pk>/generate-notes/",
        session_viewset.generate_notes,
        name="session_generate_notes",
    ),
    path("sessions/<int:pk>/save-notes/", session_viewset.save_notes, name="session_save_notes"),
    path(
        "sessions/<int:pk>/create-from-template/",
        session_viewset.create_from_template,
        name="session_create_from_template",
    ),
    # Audio processing URLs
    path("recordings/<int:pk>/transcribe/", audio_viewset.transcribe, name="transcribe"),
    path("recordings/<int:pk>/download/", audio_viewset.download, name="audio_download"),
    path("recordings/<int:pk>/delete/", audio_viewset.delete, name="audio_delete"),
]