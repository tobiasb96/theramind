from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Document URLs
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('create/', views.DocumentCreateView.as_view(), name='document_create'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('<int:pk>/edit/', views.DocumentUpdateView.as_view(), name='document_edit'),
    path('<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document_delete'),
    path('<int:pk>/save-content/', views.SaveDocumentContentView.as_view(), name='document_save_content'),
    
    # Patient-nested document URLs
    path('patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/documents/', 
         views.DocumentListView.as_view(), name='document_list_nested'),
    path('patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/documents/create/', 
         views.DocumentCreateView.as_view(), name='document_create_nested'),
    path('patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/documents/<int:pk>/', 
         views.DocumentDetailView.as_view(), name='document_detail_nested'),
    path('patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/documents/<int:pk>/edit/', 
         views.DocumentUpdateView.as_view(), name='document_edit_nested'),
    path('patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/documents/<int:pk>/delete/', 
         views.DocumentDeleteView.as_view(), name='document_delete_nested'),
    
    # Document generation URLs
    path('patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/generate/', 
         views.GenerateDocumentView.as_view(), name='generate_document'),
    path('patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/form/', 
         views.DocumentFormView.as_view(), name='document_form'),
] 