from django.urls import path
from .views import TherapyViewSet, SessionViewSet, AudioViewSet

app_name = 'therapy'

# Initialize ViewSets
therapy_viewset = TherapyViewSet()
session_viewset = SessionViewSet()
audio_viewset = AudioViewSet()

urlpatterns = [
    # Patient-nested therapy URLs
    path(
        "patients/<uuid:patient_pk>/therapies/",
        therapy_viewset.list,
        name="therapy_list",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/create/",
        therapy_viewset.create,
        name="therapy_create",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:pk>/",
        therapy_viewset.retrieve,
        name="therapy_detail",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:pk>/edit/",
        therapy_viewset.update,
        name="therapy_edit",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:pk>/delete/",
        therapy_viewset.destroy,
        name="therapy_delete",
    ),
    # Patient-nested session URLs
    path(
        "patients/<uuid:patient_pk>/sessions/create/",
        session_viewset.create,
        name="session_create_simple",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/sessions/create/",
        session_viewset.create,
        name="session_create",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/sessions/<int:session_pk>/",
        session_viewset.retrieve,
        name="session_detail",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/sessions/<int:session_pk>/edit/",
        session_viewset.update,
        name="session_edit",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/sessions/<int:session_pk>/delete/",
        session_viewset.destroy,
        name="session_delete",
    ),
    # Session custom actions
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/sessions/<int:session_pk>/upload-audio/",
        audio_viewset.upload,
        name="session_audio_upload",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/sessions/<int:session_pk>/save-transcript/",
        session_viewset.save_transcript,
        name="session_save_transcript",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/sessions/<int:session_pk>/generate-notes/",
        session_viewset.generate_notes,
        name="session_generate_notes",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/sessions/<int:session_pk>/save-notes/",
        session_viewset.save_notes,
        name="session_save_notes",
    ),
    # Audio processing URLs
    path("recordings/<int:pk>/transcribe/", audio_viewset.transcribe, name="transcribe"),
    path("recordings/<int:pk>/download/", audio_viewset.download, name="audio_download"),
    path("recordings/<int:pk>/delete/", audio_viewset.delete, name="audio_delete"),
]