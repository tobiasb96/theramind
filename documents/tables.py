import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from .models import Document, DocumentTemplate


class DocumentTable(tables.Table):
    title = tables.Column(
        verbose_name="Name", orderable=True, attrs={"td": {"class": "px-6 py-4 whitespace-nowrap"}}
    )

    created_at = tables.Column(
        verbose_name="Erstellt",
        orderable=True,
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap text-sm text-gray-500"}},
    )

    patient = tables.Column(
        verbose_name="Patient",
        accessor="therapy__patient__full_name",
        orderable=True,
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap text-sm text-gray-500"}},
    )

    actions = tables.Column(
        verbose_name="Aktionen",
        orderable=False,
        exclude_from_export=True,
        empty_values=(),
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap text-sm font-medium"}},
    )

    class Meta:
        model = Document
        template_name = "partials/table.html"
        fields = ("title", "created_at", "patient", "actions")
        attrs = {
            "class": "w-full table-auto text-md text-left rounded text-gray-900 bg-white",
            "thead": {
                "class": "text-xs text-gray-600 font-normal border border-blue-200 bg-blue-100"
            },
            "tbody": {"class": "bg-white divide-y divide-gray-200"},
        }
        empty_text = "Keine Dokumente vorhanden."
        order_by = "-created_at"  # Default ordering by most recent

    def render_created_at(self, value):
        return value.strftime("%d.%m.Y")

    def render_actions(self, record):
        detail_url = reverse('documents:document_detail', kwargs={'pk': record.pk})
        return format_html(
            '<a href="{}" class="text-blue-600 hover:text-blue-800 font-medium">Ansehen</a>',
            detail_url,
        )


class TemplateTable(tables.Table):
    name = tables.Column(
        verbose_name="Name", orderable=True, attrs={"td": {"class": "px-6 py-4 whitespace-nowrap"}}
    )

    template_type = tables.Column(
        verbose_name="Typ",
        orderable=True,
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap text-sm text-gray-500"}},
    )

    status = tables.Column(
        verbose_name="Status",
        orderable=False,
        empty_values=(),
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap text-sm text-gray-500"}},
    )

    created_at = tables.Column(
        verbose_name="Erstellt",
        orderable=True,
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap text-sm text-gray-500"}},
    )

    actions = tables.Column(
        verbose_name="Aktionen",
        orderable=False,
        exclude_from_export=True,
        empty_values=(),
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap text-sm font-medium"}},
    )

    class Meta:
        model = DocumentTemplate
        template_name = "partials/table.html"
        fields = ("name", "template_type", "status", "created_at", "actions")
        attrs = {
            "class": "w-full table-auto text-md text-left rounded text-gray-900 bg-white",
            "thead": {
                "class": "text-xs text-gray-600 font-normal border border-blue-200 bg-blue-100"
            },
            "tbody": {"class": "bg-white divide-y divide-gray-200"},
        }
        empty_text = "Keine Vorlagen vorhanden."
        order_by = "name"  # Default ordering by name

    def render_name(self, value, record):
        return format_html(
            '<div class="text-sm font-medium text-gray-900">{}</div>'
            '<div class="text-sm text-gray-500">{}</div>',
            record.name,
            record.description[:60] + "..."
            if record.description and len(record.description) > 60
            else record.description or "",
        )

    def render_template_type(self, value, record):
        color_class = (
            "bg-blue-100 text-blue-800"
            if record.template_type == "document"
            else "bg-green-100 text-green-800"
        )
        return format_html(
            '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {}">'
            "{}"
            "</span>",
            color_class,
            record.get_template_type_display(),
        )

    def render_status(self, value, record):
        if record.is_predefined:
            return format_html(
                '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">'
                "Vordefiniert"
                "</span>"
            )
        else:
            return format_html(
                '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">'
                "Benutzerdefiniert"
                "</span>"
            )

    def render_created_at(self, value):
        return value.strftime("%d.%m.Y")

    def render_actions(self, record):
        detail_url = reverse("documents:template_detail", kwargs={"pk": record.pk})
        edit_url = reverse("documents:template_edit", kwargs={"pk": record.pk})
        clone_url = reverse("documents:template_clone", kwargs={"pk": record.pk})

        actions_html = f'<a href="{detail_url}" class="text-blue-600 hover:text-blue-800 font-medium mr-2">Ansehen</a>'

        if not record.is_predefined:
            actions_html += f'<a href="{edit_url}" class="text-indigo-600 hover:text-indigo-800 font-medium mr-2">Bearbeiten</a>'

        # For the clone action, we'll create a simpler approach without inline form
        actions_html += f'<a href="{clone_url}?name={record.name}%20(Kopie)" class="text-green-600 hover:text-green-800 font-medium" onclick="return confirm(\'Vorlage klonen?\')">Klonen</a>'

        return format_html(actions_html)
