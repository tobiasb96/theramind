from django.urls import path
from . import views

app_name = 'therapy'

urlpatterns = [
    # Therapy URLs
    path('', views.TherapyListView.as_view(), name='therapy_list'),
    path('create/', views.TherapyCreateView.as_view(), name='therapy_create'),
    path('<int:pk>/', views.TherapyDetailView.as_view(), name='therapy_detail'),
    path('<int:pk>/edit/', views.TherapyUpdateView.as_view(), name='therapy_edit'),
    path('<int:pk>/delete/', views.TherapyDeleteView.as_view(), name='therapy_delete'),
    
    # Session URLs
    path('sessions/', views.SessionListView.as_view(), name='session_list'),
    path('sessions/create/', views.SessionCreateView.as_view(), name='session_create'),
    path('sessions/<int:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('sessions/<int:pk>/edit/', views.SessionUpdateView.as_view(), name='session_edit'),
    path('sessions/<int:pk>/delete/', views.SessionDeleteView.as_view(), name='session_delete'),
    path('sessions/<int:pk>/upload-audio/', views.AudioUploadView.as_view(), name='audio_upload'),
    
    # Document URLs
    path('documents/', views.DocumentListView.as_view(), name='document_list'),
    path('documents/create/', views.DocumentCreateView.as_view(), name='document_create'),
    path('documents/<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('documents/<int:pk>/edit/', views.DocumentUpdateView.as_view(), name='document_edit'),
    path('documents/<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document_delete'),
    
    # Audio processing URLs
    path('recordings/<int:pk>/transcribe/', views.TranscribeView.as_view(), name='transcribe'),
    path('recordings/<int:pk>/download/', views.AudioDownloadView.as_view(), name='audio_download'),
]