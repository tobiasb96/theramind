from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import update_session_auth_hash
from .models import UserSettings
from .forms import ProfileUpdateForm, UserSettingsForm


class LoginView(auth_views.LoginView):
    """Custom login view using Django's built-in authentication"""
    template_name = 'users/login.html'
    form_class = AuthenticationForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('core:dashboard')


class LogoutView(auth_views.LogoutView):
    """Custom logout view"""
    next_page = reverse_lazy('users:login')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ensure user has settings (create if not exists)
        settings, created = UserSettings.objects.get_or_create(user=self.request.user)
        context["user_settings"] = settings

        # Add forms to context
        context["profile_form"] = ProfileUpdateForm(
            instance=self.request.user, user=self.request.user
        )
        context["settings_form"] = UserSettingsForm(instance=settings)

        # Check if we should show the settings tab
        context["show_settings_tab"] = self.request.GET.get("tab") == "settings"

        return context


@method_decorator(login_required, name='dispatch')
class ChangePasswordView(View):
    """View for changing user password"""
    
    def post(self, request):
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        # Validate current password
        if not request.user.check_password(current_password):
            messages.error(request, 'Das aktuelle Passwort ist falsch.')
            return redirect('users:profile')
        
        # Validate new passwords match
        if new_password1 != new_password2:
            messages.error(request, 'Die neuen Passwörter stimmen nicht überein.')
            return redirect('users:profile')
        
        # Validate new password is not empty
        if not new_password1:
            messages.error(request, 'Das neue Passwort darf nicht leer sein.')
            return redirect('users:profile')
        
        # Use Django's built-in password validation
        try:
            validate_password(new_password1, request.user)
        except ValidationError as e:
            # Use Django's error codes for stable, locale-independent error handling
            for error in e.error_list:
                if hasattr(error, "code"):
                    if error.code == "password_too_short":
                        messages.error(
                            request, "Das neue Passwort muss mindestens 8 Zeichen lang sein."
                        )
                    elif error.code == "password_too_similar":
                        messages.error(
                            request,
                            "Das neue Passwort ist zu ähnlich zu Deinen persönlichen Informationen.",
                        )
                    elif error.code == "password_too_common":
                        messages.error(request, "Das neue Passwort ist zu häufig verwendet.")
                    elif error.code == "password_entirely_numeric":
                        messages.error(
                            request, "Das neue Passwort darf nicht nur aus Zahlen bestehen."
                        )
                    else:
                        messages.error(request, str(error))
                else:
                    # Fallback for errors without codes
                    messages.error(request, str(error))
            return redirect('users:profile')
        
        # Set new password
        request.user.set_password(new_password1)
        request.user.save()

        # Update session to prevent logout after password change
        update_session_auth_hash(request, request.user)

        messages.success(request, "Dein Passwort wurde erfolgreich geändert.")
        return redirect('users:profile')


@method_decorator(login_required, name="dispatch")
class UpdateProfileView(View):
    """View for updating user profile information using forms"""

    def post(self, request):
        form = ProfileUpdateForm(request.POST, instance=request.user, user=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Profil wurde erfolgreich aktualisiert.")
        else:
            # Handle form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")

        return redirect("users:profile")


@method_decorator(login_required, name="dispatch")
class UpdateSettingsView(View):
    """View for updating user settings using forms"""

    def post(self, request):
        settings, created = UserSettings.objects.get_or_create(user=request.user)
        form = UserSettingsForm(request.POST, instance=settings)

        if form.is_valid():
            form.save()
            messages.success(request, "Einstellungen wurden erfolgreich gespeichert.")
        else:
            # Handle form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")

        # Redirect to profile page with settings tab active
        profile_url = reverse("users:profile")
        return redirect(f"{profile_url}?tab=settings")
