from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserManager(BaseUserManager):
    """
    Django requires that custom users define their own Manager class. By
    inheriting from `BaseUserManager`, we get a lot of the same code used by
    Django to create a `User`.

    All we have to do is override the `create_user` function which we will use
    to create `User` objects.
    """

    def create_user(self, email: str, password: str, first_name: str = None, last_name: str = None):
        """
        Create and return a `User` with an email and name.
        """
        normalized_email = self.normalize_email(email)
        user = self.model(
            email=normalized_email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email: str, password: str, first_name: str = None, last_name: str = None):
        """
        Create and return a `User` with superuser (admin) permissions.
        """
        if not first_name:
            first_name = "Admin"
        if not last_name:
            last_name = "User"
            
        user = self.create_user(email, password, first_name, last_name)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    # Each `User` needs a human-readable unique identifier that we can use to
    # represent the `User` in the UI. We want to index this column in the
    # database to improve lookup performance.
    # username = models.CharField(db_index=True, max_length=255, unique=True, null=True, default=None)  # noqa: E501

    # We also need a way to contact the users and a way for the users to identify
    # themselves when logging in. Since we need an email address for contacting
    # the users anyways, we will also use the email for logging in because it is
    # the most common form of login credential at the time of writing.
    email = models.EmailField(db_index=True, unique=True)

    # When a users no longer wishes to use our platform, they may try to delete
    # their account. That's a problem for us because the data we collect is
    # valuable to us and we don't want to delete it. We
    # will simply offer users a way to deactivate their account instead of
    # letting them delete it. That way they won't show up on the site anymore,
    # but we can still analyze the data.
    is_active = models.BooleanField(default=True)

    # The `is_staff` flag is expected by Django to determine who can and cannot
    # log into the Django admin site. For most users this flag will always be
    # false.
    is_staff = models.BooleanField(default=False)

    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True)

    # A timestamp representing when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    # Custom fields
    first_name = models.CharField(max_length=255, null=True, default=None)
    last_name = models.CharField(max_length=255, null=True, default=None)

    # The `USERNAME_FIELD` property tells us which field we will use to log in.
    # In this case we want it to be the email field.
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        """
        Returns a string representation of this `User`.

        This string is used when a `User` is printed in the console.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.email

    def save(self, *args, **kwargs):
        """Create user settings when user is created"""
        is_new_user = not self.pk
        super().save(*args, **kwargs)
        if is_new_user:
            UserSettings.objects.create(user=self)


class UserSettings(models.Model):
    """User settings for transcription and report generation preferences"""

    GENDER_CHOICES = [
        ("weiblich", "Weiblich"),
        ("männlich", "Männlich"),
        ("divers", "Divers"),
    ]

    PATIENT_FOCUS_CHOICES = [
        ("erwachsene", "Erwachsene (PP)"),
        ("kinder", "Kinder und Jugendliche (KJP)"),
    ]

    THERAPY_FOCUS_CHOICES = [
        ("ap", "Psychoanalyse (AP)"),
        ("st", "Systemische Therapie (ST)"),
        ("tp", "Tiefenpsychologie (TP)"),
        ("vt", "Verhaltenstherapie (VT)"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default="weiblich")
    patient_focus = models.CharField(
        max_length=20, choices=PATIENT_FOCUS_CHOICES, default="erwachsene"
    )
    therapy_focus = models.CharField(max_length=20, choices=THERAPY_FOCUS_CHOICES, default="vt")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Settings"
        verbose_name_plural = "User Settings"

    def __str__(self):
        return f"Settings for {self.user}"
