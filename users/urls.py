from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change_password"),
    path("update-profile/", views.UpdateProfileView.as_view(), name="update_profile"),
    path("update-settings/", views.UpdateSettingsView.as_view(), name="update_settings"),
] 