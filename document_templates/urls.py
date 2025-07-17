from django.urls import path
from .views import TemplateViewSet

app_name = 'document_templates'

# Initialize ViewSets
template_viewset = TemplateViewSet()

urlpatterns = [
    # Template URLs
    path("", template_viewset.list, name="template_list"),
    path("create/", template_viewset.create, name="template_create"),
    path("<int:pk>/", template_viewset.retrieve, name="template_detail"),
    path("<int:pk>/edit/", template_viewset.update, name="template_edit"),
    path("<int:pk>/delete/", template_viewset.destroy, name="template_delete"),
    path("<int:pk>/clone/", template_viewset.clone, name="template_clone"),
] 