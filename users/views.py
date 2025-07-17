from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.views.generic import TemplateView


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
