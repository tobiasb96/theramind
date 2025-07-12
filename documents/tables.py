import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from .models import Document
from .prompts import get_available_document_types


class DocumentTable(tables.Table):
    title = tables.Column(
        verbose_name="Name",
        orderable=True,
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap"}}
    )
    
    created_at = tables.Column(
        verbose_name="Erstellt",
        orderable=True,
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap text-sm text-gray-500"}}
    )
    
    patient = tables.Column(
        verbose_name="Patient",
        accessor="therapy__patient__full_name",
        orderable=True,
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap text-sm text-gray-500"}}
    )
    
    document_type = tables.Column(
        verbose_name="Typ",
        orderable=True,
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap text-sm text-gray-500"}}
    )
    
    actions = tables.Column(
        verbose_name="Aktionen",
        orderable=False,
        exclude_from_export=True,
        empty_values=(),
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap text-sm font-medium"}}
    )

    class Meta:
        model = Document
        template_name = "partials/table.html"
        fields = ("title", "created_at", "patient", "document_type", "actions")
        attrs = {
            "class": "w-full table-auto text-md text-left rounded text-gray-900 bg-white",
            "thead": {
                "class": "text-xs text-gray-600 font-normal border border-blue-200 bg-blue-100"
            },
            "tbody": {
                "class": "bg-white divide-y divide-gray-200"
            }
        }
        empty_text = "Keine Dokumente vorhanden."
        order_by = "-created_at"  # Default ordering by most recent

    def render_created_at(self, value):
        return value.strftime("%d.%m.%Y")

    def render_document_type(self, value):
        document_types = get_available_document_types()
        type_name = document_types.get(value, value)
        return format_html(
            '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">'
            '{}'
            '</span>',
            type_name
        )

    def render_actions(self, record):
        detail_url = reverse('documents:document_detail', kwargs={'pk': record.pk})
        return format_html(
            '<a href="{}" class="text-blue-600 hover:text-blue-800 font-medium">'
            'Ansehen'
            '</a>',
            detail_url
        ) 