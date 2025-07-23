from django.urls import path
from .views import ReportViewSet

app_name = 'reports'

# Initialize ViewSets
report_viewset = ReportViewSet()

urlpatterns = [
    # Report URLs
    path("create/", report_viewset.create, name="report_create"),
    path("<int:pk>/", report_viewset.retrieve, name="report_detail"),
    path("<int:pk>/edit/", report_viewset.update, name="report_edit"),
    path("<int:pk>/delete/", report_viewset.destroy, name="report_delete"),
    path("<int:pk>/generate-content/", report_viewset.generate_content, name="generate_content"),
    path("<int:pk>/save-content/", report_viewset.save_content, name="save_content"),
    path(
        "<int:pk>/create-from-template/",
        report_viewset.create_from_template,
        name="report_create_from_template",
    ),
    # Export
    path("<int:pk>/export/pdf/", report_viewset.export_pdf, name="report_export_pdf"),
] 