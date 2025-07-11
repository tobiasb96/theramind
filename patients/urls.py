from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('patients/', views.PatientListView.as_view(), name='patient_list'),
    path('patients/create/', views.PatientCreateView.as_view(), name='patient_create'),
    path('patients/<uuid:pk>/', views.PatientDetailView.as_view(), name='patient_detail'),
    path('patients/<uuid:pk>/edit/', views.PatientUpdateView.as_view(), name='patient_edit'),
    path('patients/<uuid:pk>/delete/', views.PatientDeleteView.as_view(), name='patient_delete'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
]