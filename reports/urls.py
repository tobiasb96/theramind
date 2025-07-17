from django.urls import path
from .views import ReportViewSet

app_name = 'reports'

# Initialize ViewSets
report_viewset = ReportViewSet()

urlpatterns = [
    # Report URLs (now standalone)
    path("", report_viewset.list, name="report_list"),
    path("create/", report_viewset.create, name="report_create"),
    path("<int:pk>/", report_viewset.retrieve, name="report_detail"),
    path("<int:pk>/edit/", report_viewset.update, name="report_edit"),
    path("<int:pk>/delete/", report_viewset.destroy, name="report_delete"),
    path("<int:pk>/export/", report_viewset.export, name="report_export"),
    path("generate/", report_viewset.generate, name="generate_report"),
] 