from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_tables2 import RequestConfig

from .models import DocumentTemplate
from .service import TemplateService

from .table import TemplateTable
from users.mixins import TemplateOwnershipMixin


class TemplateViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing custom templates
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # CRITICAL SECURITY: Show predefined templates and user's own templates only
        return DocumentTemplate.objects.filter(
            is_active=True
        ).filter(
            Q(is_predefined=True) | Q(user=self.request.user)
        ).order_by("name")

    def list(self, request):
        """List all templates"""
        template_type = request.GET.get("type", "")  # Default to empty (all types)
        templates = self.get_queryset()

        # Filter by template type if specified
        if template_type:
            templates = templates.filter(template_type=template_type)

        # Handle search
        search_query = request.GET.get("search", "")
        if search_query:
            templates = templates.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        # Create table with proper ordering
        table = TemplateTable(templates)
        RequestConfig(request, paginate={"per_page": 20}).configure(table)

        return render(
            request,
            "document_templates/template_list.html",
            {
                "templates_table": table,
                "template_type": template_type,
                "search_query": search_query,
            },
        )

    def retrieve(self, request, pk=None):
        """Retrieve a specific template"""
        # CRITICAL SECURITY: Only allow access to predefined templates or user's own templates
        template = get_object_or_404(
            DocumentTemplate, 
            pk=pk, 
            is_active=True
        )
        
        # Check if user can access this template
        if not (template.is_predefined or template.user == request.user):
            from django.http import Http404
            raise Http404("Template not found")

        return render(
            request,
            "document_templates/template_detail.html",
            {"template": template},
        )

    def create(self, request):
        """Create a new template"""
        if request.method == "GET":
            # Show template creation form
            return render(
                request,
                "document_templates/template_form.html",
                {
                    "template_types": DocumentTemplate.TEMPLATE_TYPES,
                },
            )

        elif request.method == "POST":
            # Create new template
            try:
                template_data = {
                    "name": request.POST.get("name"),
                    "description": request.POST.get("description", ""),
                    "template_type": request.POST.get("template_type"),
                    "system_prompt": "",  # Always empty, hardcoded in service
                    "user_prompt": request.POST.get("user_prompt"),
                    "max_tokens": 2000,  # Default value
                    "temperature": 0.3,  # Default value
                    "is_predefined": False,
                    "is_active": True,
                }

                template_service = TemplateService()
                # CRITICAL SECURITY: Pass user when creating template
                template = template_service.create_custom_template(template_data, user=request.user)

                messages.success(request, "Template wurde erfolgreich erstellt.")

                # Handle HTMX requests
                if request.headers.get("HX-Request"):
                    response = HttpResponse()
                    response["HX-Redirect"] = reverse_lazy(
                        "document_templates:template_detail", kwargs={"pk": template.pk}
                    )
                    return response

                return HttpResponse(
                    status=302,
                    headers={
                        "Location": reverse_lazy(
                            "document_templates:template_detail", kwargs={"pk": template.pk}
                        )
                    },
                )

            except Exception as e:
                messages.error(request, f"Fehler beim Erstellen des Templates: {str(e)}")
                return render(
                    request,
                    "document_templates/template_form.html",
                    {
                        "template_types": DocumentTemplate.TEMPLATE_TYPES,
                    },
                )

    def update(self, request, pk=None):
        """Update an existing template"""
        # CRITICAL SECURITY: Only allow editing of user's own templates (not predefined ones)
        template = get_object_or_404(
            DocumentTemplate, 
            pk=pk, 
            user=request.user,
            is_predefined=False  # Cannot edit predefined templates
        )

        if request.method == "GET":
            return render(
                request,
                "documents/template_form.html",
                {
                    "template": template,
                    "template_types": DocumentTemplate.TEMPLATE_TYPES,
                },
            )

        elif request.method == "POST":
            try:
                template.name = request.POST.get("name")
                template.description = request.POST.get("description", "")
                template.template_type = request.POST.get("template_type")
                template.user_prompt = request.POST.get("user_prompt")
                template.save()

                messages.success(request, "Template wurde erfolgreich aktualisiert.")

                # Handle HTMX requests
                if request.headers.get("HX-Request"):
                    response = HttpResponse()
                    response["HX-Redirect"] = reverse_lazy(
                        "document_templates:template_detail", kwargs={"pk": template.pk}
                    )
                    return response

                return HttpResponse(
                    status=302,
                    headers={
                        "Location": reverse_lazy(
                            "document_templates:template_detail", kwargs={"pk": template.pk}
                        )
                    },
                )

            except Exception as e:
                messages.error(request, f"Fehler beim Aktualisieren des Templates: {str(e)}")
                return render(
                    request,
                    "documents/template_form.html",
                    {
                        "template": template,
                        "template_types": DocumentTemplate.TEMPLATE_TYPES,
                    },
                )

    def destroy(self, request, pk=None):
        """Delete a template"""
        # CRITICAL SECURITY: Only allow deletion of user's own templates (not predefined ones)
        template = get_object_or_404(
            DocumentTemplate, 
            pk=pk, 
            user=request.user,
            is_predefined=False  # Cannot delete predefined templates
        )

        if request.method == "GET":
            return render(request, "documents/template_confirm_delete.html", {"template": template})

        elif request.method == "POST":
            template.delete()
            messages.success(request, "Template wurde erfolgreich gelöscht.")

            # Handle HTMX requests
            if request.headers.get("HX-Request"):
                response = HttpResponse()
                response["HX-Redirect"] = reverse_lazy("document_templates:template_list")
                return response

            return HttpResponse(
                status=302, headers={"Location": reverse_lazy("document_templates:template_list")}
            )

    @action(detail=True, methods=["get", "post"])
    def clone(self, request, pk=None):
        """Clone a template"""
        # CRITICAL SECURITY: Only allow cloning of predefined templates or user's own templates
        template = get_object_or_404(
            DocumentTemplate, 
            pk=pk, 
            is_active=True
        )
        
        # Check if user can access this template
        if not (template.is_predefined or template.user == request.user):
            from django.http import Http404
            raise Http404("Template not found")

        try:
            # Handle both GET and POST requests
            if request.method == "GET":
                new_name = request.GET.get("name", f"{template.name} (Kopie)")
            else:
                new_name = request.POST.get("name", f"{template.name} (Kopie)")

            template_service = TemplateService()
            # CRITICAL SECURITY: Pass user when cloning template
            cloned_template = template_service.clone_template(template.id, new_name, user=request.user)

            messages.success(request, f"Template '{new_name}' wurde erfolgreich erstellt.")

            # Handle HTMX requests
            if request.headers.get("HX-Request"):
                response = HttpResponse()
                response["HX-Redirect"] = reverse_lazy(
                    "document_templates:template_detail", kwargs={"pk": cloned_template.pk}
                )
                return response

            return HttpResponse(
                status=302,
                headers={
                    "Location": reverse_lazy(
                        "document_templates:template_detail", kwargs={"pk": cloned_template.pk}
                    )
                },
            )

        except Exception as e:
            messages.error(request, f"Fehler beim Klonen des Templates: {str(e)}")
            return HttpResponse(
                status=302,
                headers={
                    "Location": reverse_lazy(
                        "document_templates:template_detail", kwargs={"pk": template.pk}
                    )
                },
            )