import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from .models import Patient


class PatientTable(tables.Table):
    full_name = tables.Column(
        verbose_name="Name",
        accessor="last_name",  # Order by last name for better sorting
        orderable=False,
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap"}}
    )
    
    email = tables.Column(
        verbose_name="E-Mail",
        orderable=False,
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap text-sm text-gray-500"}}
    )
    
    phone = tables.Column(
        verbose_name="Telefon",
        orderable=False,
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap text-sm text-gray-500"}}
    )
    
    session_count = tables.Column(
        verbose_name="Sitzungen",
        orderable=False,
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
        model = Patient
        fields = ("full_name", "email", "phone", "session_count", "actions")
        attrs = {
            "class": "w-full table-auto text-md text-left rounded text-gray-900 bg-white",
            "thead": {
                "class": "text-xs text-gray-600 font-normal border border-blue-200 bg-blue-100"
            },
            "tbody": {
                "class": "bg-white divide-y divide-gray-200"
            }
        }
        empty_text = "Keine Patienten vorhanden."
        order_by = "last_name"  # Default ordering

    def render_full_name(self, value, record):
        return format_html(
            '<div class="text-sm font-medium text-gray-900">{}</div>'
            '<div class="text-sm text-gray-500">{}</div>',
            record.full_name,
            record.created_at.strftime("%d.%m.%Y")
        )

    def render_email(self, value):
        return value or "-"

    def render_phone(self, value):
        return value or "-"

    def render_created_at(self, value):
        return value.strftime("%d.%m.%Y")

    def render_actions(self, record):
        detail_url = reverse('patients:patient_detail', kwargs={'pk': record.pk})
        return format_html(
            '<a href="{}" class="text-blue-600 hover:text-blue-800 font-medium">'
            'Ansehen'
            '</a>',
            detail_url
        ) 