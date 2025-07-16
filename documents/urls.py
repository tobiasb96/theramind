from django.urls import path
from .views import DocumentViewSet, TemplateViewSet

app_name = 'documents'

# Initialize ViewSets
document_viewset = DocumentViewSet()
template_viewset = TemplateViewSet()

urlpatterns = [
    # Document URLs
    path("", document_viewset.list, name="document_list"),
    path("create/", document_viewset.create, name="document_create"),
    path("<int:pk>/", document_viewset.retrieve, name="document_detail"),
    path("<int:pk>/edit/", document_viewset.update, name="document_edit"),
    path("<int:pk>/delete/", document_viewset.destroy, name="document_delete"),
    path("<int:pk>/export/", document_viewset.export, name="document_export"),
    # Template URLs
    path("templates/", template_viewset.list, name="template_list"),
    path("templates/create/", template_viewset.create, name="template_create"),
    path("templates/<int:pk>/", template_viewset.retrieve, name="template_detail"),
    path("templates/<int:pk>/edit/", template_viewset.update, name="template_edit"),
    path("templates/<int:pk>/delete/", template_viewset.destroy, name="template_delete"),
    path("templates/<int:pk>/clone/", template_viewset.clone, name="template_clone"),
    # Patient-nested document URLs
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/documents/",
        document_viewset.list,
        name="document_list_nested",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/documents/create/",
        document_viewset.create,
        name="document_create_nested",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/documents/<int:pk>/",
        document_viewset.retrieve,
        name="document_detail_nested",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/documents/<int:pk>/edit/",
        document_viewset.update,
        name="document_edit_nested",
    ),
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/documents/<int:pk>/delete/",
        document_viewset.destroy,
        name="document_delete_nested",
    ),
    # Document generation URLs
    path(
        "patients/<uuid:patient_pk>/therapies/<int:therapy_pk>/generate/",
        document_viewset.generate,
        name="generate_document",
    ),
] 