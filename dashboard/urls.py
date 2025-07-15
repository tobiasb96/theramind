from django.urls import path
from .views import DashboardView, QuickSessionCreateView, QuickDocumentCreateView

app_name = "core"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("quick-session/", QuickSessionCreateView.as_view(), name="quick_session_create"),
    path("quick-document/", QuickDocumentCreateView.as_view(), name="quick_document_create"),
]