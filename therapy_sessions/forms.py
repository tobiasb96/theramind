from django import forms
from .models import Session
from users.mixins import UserFormMixin


class SessionForm(UserFormMixin, forms.ModelForm):
    class Meta:
        model = Session
        fields = ["date", "title", "patient_gender"]
        widgets = {
            "date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "patient_gender": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
