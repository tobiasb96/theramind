from django import forms
from .models import AudioInput, DocumentInput


class AudioInputForm(forms.ModelForm):
    """Form for uploading audio files"""
    
    therapeutic_observations = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
            "rows": 4,
            "placeholder": "Notiere hier zusätzliche therapeutische Beobachtungen..."
        }),
        label="Therapeutische Beobachtungen"
    )
    
    class Meta:
        model = AudioInput
        fields = ["audio_file"]
        widgets = {
            "audio_file": forms.FileInput(attrs={
                "class": "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100",
                "accept": "audio/*"
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["audio_file"].label = "Audio-Datei"


class DocumentFileInputForm(forms.ModelForm):
    """Form for uploading document files"""
    
    class Meta:
        model = DocumentInput
        fields = ["document_file"]
        widgets = {
            "document_file": forms.FileInput(attrs={
                "class": "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100",
                "accept": ".pdf,.docx,.doc,.txt"
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["document_file"].label = "Datei auswählen"
        self.fields["document_file"].help_text = "Unterstützte Formate: PDF, Word (.docx, .doc), Text (.txt)"


class DocumentTextInputForm(forms.ModelForm):
    """Form for manual text input"""
    
    text_content = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
            "rows": 15,
            "placeholder": "Gib hier den Text ein, der als Kontext verwendet werden soll..."
        }),
        label="Text-Inhalt",
        help_text="Gib den Text direkt ein, der verarbeitet werden soll."
    )
    
    class Meta:
        model = DocumentInput
        fields = [] 