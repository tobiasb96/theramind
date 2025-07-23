from django.core.management.base import BaseCommand
from django.db import transaction
from document_templates.models import DocumentTemplate
from document_templates.template_content.reports import REPORT_TEMPLATES
from document_templates.template_content.sessions import SESSION_TEMPLATES


class Command(BaseCommand):
    help = 'Seed document templates from existing prompts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of existing templates',
        )

    def handle(self, *args, **options):
        force = options['force']

        with transaction.atomic():
            # Session notes templates from therapy_sessions/prompts.py
            session_templates = [
                {
                    'name': 'Sitzungsnoriz',
                    'description': 'Strukturierte Sitzungsdokumentation aus Therapietranskript mit klinischer, objektiver Sprache und psychologischen Fachbegriffen',
                    'template_type': 'session_notes',
                    'user_prompt': SESSION_TEMPLATES.get("session_notes"),
                    'max_tokens': 2500,
                    'temperature': 0.3,
                    'is_predefined': True,
                    'is_active': True,
                },
                {
                    'name': 'Sitzungsnotiz (kurz)',
                    'description': 'Kompakte strukturierte Sitzungsdokumentation aus Therapietranskript mit klinischer Sprache und Fokus auf therapeutisch relevante Inhalte',
                    'template_type': 'session_notes',
                    'user_prompt': SESSION_TEMPLATES.get("session_notes_short"),
                    'max_tokens': 1500,
                    'temperature': 0.3,
                    'is_predefined': True,
                    'is_active': True,
                },
                {
                    'name': 'Erstgespräch',
                    'description': 'Strukturierte Dokumentation des Erstgesprächs mit umfassender Anamnese und diagnostischer Einschätzung in professionellem psychotherapeutischem Stil',
                    'template_type': 'session_notes',
                    'user_prompt': SESSION_TEMPLATES.get("initial_consultation"),
                    'max_tokens': 3000,
                    'temperature': 0.3,
                    'is_predefined': True,
                    'is_active': True,
                },
                {
                    'name': 'Biographische Anamnese',
                    'description': 'Strukturierte biographische Anamnese mit Fokus auf prägende Ereignisse und Entwicklungsstufen der psychischen und emotionalen Entwicklung',
                    'template_type': 'session_notes',
                    'user_prompt': SESSION_TEMPLATES.get("biographical_anamnesis"),
                    'max_tokens': 2500,
                    'temperature': 0.3,
                    'is_predefined': True,
                    'is_active': True,
                },
            ]

            # Create or update session notes templates
            for template_data in session_templates:
                template_name = template_data['name']
                template_type = template_data['template_type']

                if force:
                    # Delete existing template if force is True
                    DocumentTemplate.objects.filter(
                        name=template_name,
                        template_type=template_type,
                        is_predefined=True
                    ).delete()

                # Create template if it doesn't exist
                template, created = DocumentTemplate.objects.get_or_create(
                    name=template_name,
                    template_type=template_type,
                    is_predefined=True,
                    defaults=template_data
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Created session notes template: {template_name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Session notes template already exists: {template_name}')
                    )

            # Basic report templates
            report_templates = [
                {
                    'name': 'Erstbericht',
                    'description': 'Strukturierter Erstbericht für Kostenträger mit umfassender Darstellung der Diagnose, Anamnese und Behandlungsplanung',
                    'template_type': 'report',
                    'user_prompt': REPORT_TEMPLATES.get("intial_report"),
                    'max_tokens': 3500,
                    'temperature': 0.3,
                    'is_predefined': True,
                    'is_active': True,
                },
                {
                    'name': 'Psychologischer Befundbericht',
                    'description': 'Strukturierter psychologischer Befundbericht mit detaillierter Darstellung des psychischen Zustands und diagnostischer Einschätzung',
                    'template_type': 'report',
                    'user_prompt': REPORT_TEMPLATES.get("psychological_findings_report"),
                    'max_tokens': 4000,
                    'temperature': 0.3,
                    'is_predefined': True,
                    'is_active': True,
                },
            ]

            # Create or update report templates
            for template_data in report_templates:
                template_name = template_data['name']
                template_type = template_data['template_type']

                if force:
                    # Delete existing template if force is True
                    DocumentTemplate.objects.filter(
                        name=template_name,
                        template_type=template_type,
                        is_predefined=True
                    ).delete()

                # Create template if it doesn't exist
                template, created = DocumentTemplate.objects.get_or_create(
                    name=template_name,
                    template_type=template_type,
                    is_predefined=True,
                    defaults=template_data
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Created report template: {template_name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Report template already exists: {template_name}')
                    )

        # Summary
        session_count = DocumentTemplate.objects.filter(template_type='session_notes', is_predefined=True).count()
        report_count = DocumentTemplate.objects.filter(template_type='report', is_predefined=True).count()

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTemplate seeding completed! '
                f'Session notes templates: {session_count}, Report templates: {report_count}'
            )
        )
