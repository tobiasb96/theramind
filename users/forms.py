from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import UserSettings

User = get_user_model()


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile information"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5',
                'placeholder': 'Vorname eingeben'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5',
                'placeholder': 'Nachname eingeben'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5',
                'placeholder': 'E-Mail eingeben'
            }),
        }
        labels = {
            'first_name': 'Vorname',
            'last_name': 'Nachname',
            'email': 'E-Mail-Adresse',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.user.pk if self.user else None).exists():
            raise ValidationError('Diese E-Mail-Adresse wird bereits verwendet.')
        return email


class UserSettingsForm(forms.ModelForm):
    """Form for updating user settings"""
    
    class Meta:
        model = UserSettings
        fields = ['gender', 'patient_focus', 'therapy_focus']
        widgets = {
            'gender': forms.RadioSelect(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 focus:ring-2'
            }),
            'patient_focus': forms.RadioSelect(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 focus:ring-2'
            }),
            'therapy_focus': forms.RadioSelect(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 focus:ring-2'
            }),
        }
        labels = {
            "gender": "Geschlecht",
            "patient_focus": "Patientenfokus",
            "therapy_focus": "Therapeutische Vertiefung",
        } 