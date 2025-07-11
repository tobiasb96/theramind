from django.urls import path
from transcriptions import views

app_name = 'transcriptions'

urlpatterns = [
    path('transcribe/<int:recording_id>/', views.TranscribeAudioView.as_view(), name='transcribe'),
    path('summarize/<int:session_id>/', views.SummarizeSessionView.as_view(), name='summarize'),
]