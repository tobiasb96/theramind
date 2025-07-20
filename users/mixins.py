from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404


class UserOwnershipMixin(LoginRequiredMixin):
    """
    Mixin that ensures objects belong to the current user.
    
    This is a critical security mixin that MUST be used on all views
    that access user-specific data to prevent data leaks.
    """
    
    def get_queryset(self):
        """Filter queryset to only include objects belonging to the current user"""
        queryset = super().get_queryset()
        
        # Get the user field name - can be 'user' or 'created_by' etc.
        user_field = getattr(self, 'user_field', 'user')
        
        # Build the filter dynamically
        filter_kwargs = {user_field: self.request.user}
        
        return queryset.filter(**filter_kwargs)
    
    def get_object(self, queryset=None):
        """
        Get object and ensure it belongs to the current user.
        Raises 404 instead of permission denied to avoid revealing object existence.
        """
        obj = super().get_object(queryset)
        
        # Get the user field name
        user_field = getattr(self, 'user_field', 'user')
        
        # Check ownership
        if hasattr(obj, user_field):
            obj_user = getattr(obj, user_field)
            if obj_user != self.request.user:
                raise Http404("Object not found")
        else:
            # If no user field, check if object has a related user through another model
            if hasattr(self, 'check_user_ownership'):
                if not self.check_user_ownership(obj):
                    raise Http404("Object not found")
        
        return obj


class RelatedUserOwnershipMixin(LoginRequiredMixin):
    """
    Mixin for objects that don't have a direct user field but are related 
    to objects that do (e.g., AudioRecording -> Session -> User).
    """
    
    def check_user_ownership(self, obj):
        """Override this method to implement custom ownership check"""
        return True
    
    def get_object(self, queryset=None):
        """Get object and ensure related object belongs to current user"""
        obj = super().get_object(queryset)
        
        if not self.check_user_ownership(obj):
            raise Http404("Object not found")
        
        return obj


class TemplateOwnershipMixin(LoginRequiredMixin):
    """
    Special mixin for document templates that can be either:
    - Predefined (available to all users)
    - User-specific (only available to the owner)
    """
    
    def get_queryset(self):
        """Filter to show predefined templates and user's custom templates"""
        queryset = super().get_queryset()
        
        # Show predefined templates OR user's own templates
        from django.db.models import Q
        return queryset.filter(
            Q(is_predefined=True) | Q(user=self.request.user)
        )
    
    def get_object(self, queryset=None):
        """Get object and ensure it's either predefined or belongs to user"""
        obj = super().get_object(queryset)
        
        # Allow access to predefined templates or user's own templates
        if not (obj.is_predefined or obj.user == self.request.user):
            raise Http404("Template not found")
        
        return obj


class UserFormMixin:
    """
    Mixin for forms that automatically sets the user field when saving
    """
    
    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        """Save the form and set the user field automatically"""
        instance = super().save(commit=False)
        
        # Set user field if not already set
        if hasattr(instance, 'user') and not instance.user:
            instance.user = self.user
        
        if commit:
            instance.save()
        
        return instance