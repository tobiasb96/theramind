from django.urls import path
from .views import UnifiedInputViewSet

app_name = 'inputs'

# Initialize ViewSet
input_viewset = UnifiedInputViewSet()

urlpatterns = [
    # Audio input endpoints
    path('inputs/<str:document_type>/<int:document_id>/add-audio/', 
         input_viewset.add_audio, 
         name='add_audio_input'),
    
    # Document input endpoints
    path('inputs/<str:document_type>/<int:document_id>/add-document-file/', 
         input_viewset.add_document_file, 
         name='add_document_file_input'),
    
    path('inputs/<str:document_type>/<int:document_id>/add-document-text/', 
         input_viewset.add_document_text, 
         name='add_document_text_input'),
    
    # Delete endpoints
    path('inputs/audio/<int:pk>/delete/', 
         input_viewset.delete_audio, 
         name='delete_audio_input'),
    
    path('inputs/document/<int:pk>/delete/', 
         input_viewset.delete_document, 
         name='delete_document_input'),
] 