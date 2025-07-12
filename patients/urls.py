from django.urls import path
from .views import PatientViewSet, SettingsView

app_name = 'patients'

# Initialize ViewSet
patient_viewset = PatientViewSet()

urlpatterns = [
    path("patients/", patient_viewset.list, name="patient_list"),
    path("patients/create/", patient_viewset.create, name="patient_create"),
    path("patients/<uuid:pk>/", patient_viewset.retrieve, name="patient_detail"),
    path("patients/<uuid:pk>/edit/", patient_viewset.update, name="patient_edit"),
    path("patients/<uuid:pk>/delete/", patient_viewset.destroy, name="patient_delete"),
    path("settings/", SettingsView.as_view(), name="settings"),
]