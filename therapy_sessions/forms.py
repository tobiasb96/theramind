from django import forms
from .models import Session, AudioRecording
from users.mixins import UserFormMixin


class SessionForm(UserFormMixin, forms.ModelForm):

    class Meta:
        model = Session
        fields = ["date", "title"]
        widgets = {
            "date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AudioUploadForm(forms.ModelForm):
    class Meta:
        model = AudioRecording
        fields = ['audio']
        widgets = {
            'audio': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'audio/*'
            })
        }