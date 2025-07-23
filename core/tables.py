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
        """Render document type with colored tag"""
        if isinstance(record, Report):
            return format_html(
                '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">'
                '<svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">'
                '<path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd"/>'
                '</svg>'
                'Bericht'
                '</span>'
            )
        elif isinstance(record, Session):
            return format_html(
                '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">'
                '<svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">'
                '<path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9v3a5.006 5.006 0 0 1-5 5h-4a5.006 5.006 0 0 1-5-5V9m7 9v3m-3 0h6M11 3h2a3 3 0 0 1 3 3v5a3 3 0 0 1-3 3h-2a3 3 0 0 1-3-3V6a3 3 0 0 1 3-3Z"/>'
                '</svg>'
                'Sitzung'
                '</span>'
            )
        return "Unbekannt"

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