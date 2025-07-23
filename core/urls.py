from django.urls import path

from core.views import DocumentsListView, UnifiedInputViewSet
from dashboard.views import DashboardView, QuickDocumentCreateView, QuickSessionCreateView


app_name = "core"
input_viewset = UnifiedInputViewSet()

urlpatterns = [
    # Audio input endpoints
    path(
        "inputs/<str:document_type>/<int:document_id>/add-audio/",
        input_viewset.add_audio,
        name="add_audio_input",
    ),
    # Document input endpoints
    path(
        "inputs/<str:document_type>/<int:document_id>/add-document-file/",
        input_viewset.add_document_file,
        name="add_document_file_input",
    ),
    path(
        "inputs/<str:document_type>/<int:document_id>/add-document-text/",
        input_viewset.add_document_text,
        name="add_document_text_input",
    ),
    # Delete endpoints
    path("inputs/audio/<int:pk>/delete/", input_viewset.delete_audio, name="delete_audio_input"),
    path(
        "inputs/document/<int:pk>/delete/",
        input_viewset.delete_document,
        name="delete_document_input",
    ),
    path("", DashboardView.as_view(), name="dashboard"),
    path("documents/", DocumentsListView.as_view(), name="documents_list"),
    path("quick-session-create/", QuickSessionCreateView.as_view(), name="quick_session_create"),
    path("quick-document-create/", QuickDocumentCreateView.as_view(), name="quick_document_create"),
]
