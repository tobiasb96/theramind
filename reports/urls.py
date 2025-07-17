from django.urls import path
from .views import ReportViewSet

app_name = 'reports'

# Initialize ViewSets
report_viewset = ReportViewSet()

urlpatterns = [
    # Report URLs
    path("", report_viewset.list, name="reports_list"),
    path("create/", report_viewset.create, name="report_create"),
    path("<int:pk>/", report_viewset.retrieve, name="report_detail"),
    path("<int:pk>/edit/", report_viewset.update, name="report_edit"),
    path("<int:pk>/delete/", report_viewset.destroy, name="report_delete"),
    path("<int:pk>/export/", report_viewset.export, name="report_export"),
    # Context file management
    path(
        "<int:pk>/upload-context-file/",
        report_viewset.upload_context_file,
        name="upload_context_file",
    ),
    path("<int:pk>/add-context-text/", report_viewset.add_context_text, name="add_context_text"),
    path(
        "<int:pk>/delete-context-file/",
        report_viewset.delete_context_file,
        name="delete_context_file",
    ),
    # Content generation and saving
    path("<int:pk>/generate-content/", report_viewset.generate_content, name="generate_content"),
    path("<int:pk>/save-content/", report_viewset.save_content, name="save_content"),
    path(
        "<int:pk>/create-from-template/",
        report_viewset.create_from_template,
        name="report_create_from_template",
    ),
] 