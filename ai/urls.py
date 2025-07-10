from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('test/', views.TestAIView.as_view(), name='test'),
    path('transcribe/<int:recording_id>/', views.TranscribeAudioView.as_view(), name='transcribe'),
    path('summarize/<int:session_id>/', views.SummarizeSessionView.as_view(), name='summarize'),
]