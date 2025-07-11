from django.urls import path
from . import views

app_name = 'therapy'

urlpatterns = [
    # Patient-nested therapy URLs
    path(
        "patients/<uuid:patient_pk>/therapies/",
        views.TherapyListView.as_view(),
        name="therapy_list",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/create/",
        views.TherapyCreateView.as_view(),
        name="therapy_create",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:pk>/",
        views.TherapyDetailView.as_view(),
        name="therapy_detail",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:pk>/edit/",
        views.TherapyUpdateView.as_view(),
        name="therapy_edit",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:pk>/delete/",
        views.TherapyDeleteView.as_view(),
        name="therapy_delete",
    ),
    # Patient-nested session URLs
    path(
        "patients/<uuid:patient_pk>/sessions/create/",
        views.SessionCreateView.as_view(),
        name="session_create_simple",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/sessions/create/",
        views.SessionCreateView.as_view(),
        name="session_create",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/sessions/<int:session_pk>/",
        views.SessionDetailView.as_view(),
        name="session_detail",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/sessions/<int:session_pk>/edit/",
        views.SessionUpdateView.as_view(),
        name="session_edit",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/sessions/<int:session_pk>/delete/",
        views.SessionDeleteView.as_view(),
        name="session_delete",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/sessions/<int:session_pk>/upload-audio/",
        views.AudioUploadView.as_view(),
        name="session_audio_upload",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/sessions/<int:session_pk>/save-transcript/",
        views.SaveTranscriptView.as_view(),
        name="session_save_transcript",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/sessions/<int:session_pk>/generate-notes/",
        views.GenerateSessionNotesView.as_view(),
        name="session_generate_notes",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/sessions/<int:session_pk>/save-notes/",
        views.SaveSessionNotesView.as_view(),
        name="session_save_notes",
    ),

    # Audio processing URLs
    path("recordings/<int:pk>/transcribe/", views.TranscribeView.as_view(), name="transcribe"),
    path("recordings/<int:pk>/download/", views.AudioDownloadView.as_view(), name="audio_download"),
    path("recordings/<int:pk>/delete/", views.AudioDeleteView.as_view(), name="audio_delete"),
]