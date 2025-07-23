from django import forms
from django.utils import timezone
from .models import Session
from users.mixins import UserFormMixin


class SessionForm(UserFormMixin, forms.ModelForm):
    class Meta:
        model = Session
        fields = ["date", "title", "patient_gender"]
        widgets = {
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "z.B. Erstgespräch"}
            ),
            "patient_gender": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set default date to today if not editing existing session
        if not self.instance.pk:
            today = timezone.now().date()
            self.fields["date"].initial = today

        # Make title field optional but provide helpful text
        self.fields["title"].required = False
        self.fields[
            "title"
        ].help_text = "Optional - wenn leer, wird automatisch 'Sitzung vom [Datum]' verwendet"

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Set default title if empty
        if not instance.title:
            if instance.date:
                instance.title = f"Sitzung vom {instance.date.strftime('%d.%m.%Y')}"
            else:
                instance.title = f"Sitzung vom {timezone.now().strftime('%d.%m.%Y')}"

        if commit:
            instance.save()

        return instance
