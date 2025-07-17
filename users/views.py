from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


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
            # Convert validation errors to German messages
            for error in e.messages:
                if "at least 8 characters" in error:
                    messages.error(request, 'Das neue Passwort muss mindestens 8 Zeichen lang sein.')
                elif "too similar" in error:
                    messages.error(request, 'Das neue Passwort ist zu ähnlich zu Ihren persönlichen Informationen.')
                elif "too common" in error:
                    messages.error(request, 'Das neue Passwort ist zu häufig verwendet.')
                elif "entirely numeric" in error:
                    messages.error(request, 'Das neue Passwort darf nicht nur aus Zahlen bestehen.')
                else:
                    messages.error(request, error)
            return redirect('users:profile')
        
        # Set new password
        request.user.set_password(new_password1)
        request.user.save()
        
        messages.success(request, 'Ihr Passwort wurde erfolgreich geändert.')
        return redirect('users:profile')
