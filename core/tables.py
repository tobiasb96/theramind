import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from reports.models import Report
from therapy_sessions.models import Session


class BaseDocumentTable(tables.Table):
    """
    Unified table for displaying both Sessions and Reports (BaseDocument instances)
    """
    
    document_type = tables.Column(
        accessor='pk',  # Use pk as accessor since we just need the record
        verbose_name="Typ",
        orderable=False,
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap"}},
    )
    
    title = tables.Column(
        verbose_name="Name", 
        orderable=False, 
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap"}}
    )

    created_at = tables.Column(
        verbose_name="Erstellt",
        orderable=False,
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap text-sm text-gray-500"}},
    )

    actions = tables.Column(
        accessor='pk',  # Use pk as accessor since we just need the record
        verbose_name="Aktionen",
        orderable=False,
        exclude_from_export=True,
        empty_values=(),
        attrs={"td": {"class": "px-6 py-4 whitespace-nowrap text-sm font-medium"}},
    )

    class Meta:
        # Don't specify model since we're working with multiple model types
        fields = ("document_type", "title", "created_at", "actions")
        attrs = {
            "class": "w-full table-auto text-md text-left rounded text-gray-900 bg-white",
            "thead": {
                "class": "text-xs text-gray-600 font-normal border border-blue-200 bg-blue-100"
            },
            "tbody": {"class": "bg-white divide-y divide-gray-200"},
        }
        empty_text = "Keine Dokumente vorhanden."
        order_by = "-created_at"

    def render_document_type(self, record):
        """Render document type with colored tag and draft badge for unexported documents"""
        # Determine document type and base styling
        if isinstance(record, Report):
            base_badge = format_html("""
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    <svg class="w-3 h-3 mr-1 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 3v4a1 1 0 0 1-1 1H5m4 8h6m-6-4h6m4-8v16a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V7.914a1 1 0 0 1 .293-.707l3.914-3.914A1 1 0 0 1 9.914 3H18a1 1 0 0 1 1 1Z"/>
                    </svg>
                    Bericht
                </span>
            """)
        elif isinstance(record, Session):
            base_badge = format_html(
                """
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    <svg class="w-3 h-3 mr-1 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9v3a5.006 5.006 0 0 1-5 5h-4a5.006 5.006 0 0 1-5-5V9m7 9v3m-3 0h6M11 3h2a3 3 0 0 1 3 3v5a3 3 0 0 1-3 3h-2a3 3 0 0 1-3-3V6a3 3 0 0 1 3-3Z"/>
                    </svg>
                    Sitzung
                </span>
            """
            )
        else:
            return "Unbekannt"

        # Add draft badge for unexported documents
        if not record.is_exported:
            draft_badge = format_html(
                '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 ml-2">'
                '<svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">'
                '<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>'
                "</svg>"
                "Entwurf"
                "</span>"
            )
            return format_html("{} {}", base_badge, draft_badge)

        return base_badge

    def render_title(self, record):
        """Render title with fallback for sessions"""
        if isinstance(record, Session):
            return record.title or f"Sitzung vom {record.date.strftime('%d.%m.%Y')}"
        return record.title or "Ohne Titel"

    def render_created_at(self, value):
        """Render creation time in HH:MM format"""
        return value.strftime("%H:%M")

    def render_actions(self, record):
        """Render action links based on document type"""
        if isinstance(record, Report):
            detail_url = reverse('reports:report_detail', kwargs={'pk': record.pk})
        elif isinstance(record, Session):
            detail_url = reverse('sessions:session_detail', kwargs={'pk': record.pk})
        else:
            return ""
            
        return format_html(
            '<a href="{}" class="text-blue-600 hover:text-blue-800 font-medium">Ansehen</a>',
            detail_url,
        ) 