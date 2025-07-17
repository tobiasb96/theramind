from django.core.management.base import BaseCommand
from django.db import transaction
from document_templates.models import DocumentTemplate


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
                    'name': 'Erstgespräch',
                    'description': 'Strukturierte Vorlage für Erstgespräche mit Anamnese und diagnostischer Einschätzung',
                    'template_type': 'session_notes',
                    'user_prompt': '''<p><strong>ANAMNESE</strong></p>
<ul>
<li>Aktuelle Beschwerden und Symptome</li>
<li>Psychosoziale Situation</li>
<li>Biografische Informationen</li>
<li>Vorbehandlungen</li>
</ul>

<p><strong>DIAGNOSTISCHE EINSCHÄTZUNG</strong></p>
<ul>
<li>Erste Eindrücke</li>
<li>Mögliche Diagnosen</li>
<li>Risikofaktoren</li>
</ul>

<p><strong>THERAPIEZIELE</strong></p>
<ul>
<li>Hauptziele des Patienten</li>
<li>Behandlungsansatz</li>
</ul>

<p><strong>NÄCHSTE SCHRITTE</strong></p>
<ul>
<li>Empfohlene Maßnahmen</li>
<li>Terminvereinbarung</li>
</ul>''',
                    'max_tokens': 2000,
                    'temperature': 0.3,
                    'is_predefined': True,
                    'is_active': True,
                },
                {
                    'name': 'Verlaufsgespräch',
                    'description': 'Strukturierte Vorlage für Verlaufsgespräche mit Fortschrittsbeurteilung',
                    'template_type': 'session_notes',
                    'user_prompt': '''<p><strong>VERLAUF SEIT LETZTER SITZUNG</strong></p>
<ul>
<li>Veränderungen und Fortschritte</li>
<li>Schwierigkeiten und Rückschläge</li>
<li>Compliance mit Übungen/Aufgaben</li>
</ul>

<p><strong>AKTUELLE SITZUNG</strong></p>
<ul>
<li>Hauptthemen und Inhalte</li>
<li>Neue Erkenntnisse</li>
<li>Bearbeitete Problembereiche</li>
</ul>

<p><strong>FORTSCHRITT UND VERÄNDERUNGEN</strong></p>
<ul>
<li>Positive Entwicklungen</li>
<li>Verbleibende Herausforderungen</li>
<li>Erreichte Ziele</li>
</ul>

<p><strong>NÄCHSTE SCHRITTE</strong></p>
<ul>
<li>Neue Aufgaben/Übungen</li>
<li>Fokus für nächste Sitzung</li>
<li>Terminvereinbarung</li>
</ul>''',
                    'max_tokens': 2000,
                    'temperature': 0.3,
                    'is_predefined': True,
                    'is_active': True,
                },
                {
                    'name': 'Abschlussgespräch',
                    'description': 'Strukturierte Vorlage für Abschlussgespräche mit Rückfallprophylaxe',
                    'template_type': 'session_notes',
                    'user_prompt': '''<p><strong>THERAPIEFORTSCHRITT</strong></p>
<ul>
<li>Erreichte Ziele</li>
<li>Positive Veränderungen</li>
<li>Gelernte Strategien</li>
</ul>

<p><strong>AKTUELLER STATUS</strong></p>
<ul>
<li>Aktuelle Symptomatik</li>
<li>Bewältigungsfähigkeiten</li>
<li>Psychosoziale Situation</li>
</ul>

<p><strong>RÜCKFALLPROPHYLAXE</strong></p>
<ul>
<li>Risikofaktoren</li>
<li>Frühwarnzeichen</li>
<li>Bewältigungsstrategien</li>
</ul>

<p><strong>ABSCHLUSS</strong></p>
<ul>
<li>Zusammenfassung der Therapie</li>
<li>Empfehlungen für die Zukunft</li>
<li>Nachsorgeplan</li>
</ul>''',
                    'max_tokens': 2000,
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
                    'name': 'Standardbericht',
                    'description': 'Allgemeine Vorlage für Therapieberichte',
                    'template_type': 'report',
                    'user_prompt': '''<p><strong>PATIENTENINFORMATIONEN</strong></p>
<ul>
<li>Grundlegende Informationen</li>
<li>Behandlungszeitraum</li>
<li>Anzahl der Sitzungen</li>
</ul>

<p><strong>BEHANDLUNGSVERLAUF</strong></p>
<ul>
<li>Ausgangssituation</li>
<li>Therapieziele</li>
<li>Angewandte Methoden</li>
<li>Verlauf und Fortschritte</li>
</ul>

<p><strong>ERGEBNISSE</strong></p>
<ul>
<li>Erreichte Ziele</li>
<li>Symptomveränderungen</li>
<li>Bewältigungsstrategien</li>
</ul>

<p><strong>EMPFEHLUNGEN</strong></p>
<ul>
<li>Weitere Behandlung</li>
<li>Nachsorge</li>
<li>Prognose</li>
</ul>''',
                    'max_tokens': 3000,
                    'temperature': 0.3,
                    'is_predefined': True,
                    'is_active': True,
                },
                {
                    'name': 'Kurzbericht',
                    'description': 'Kompakte Vorlage für kurze Therapieberichte',
                    'template_type': 'report',
                    'user_prompt': '''<p><strong>BEHANDLUNGSÜBERSICHT</strong></p>
<ul>
<li>Behandlungszeitraum und -umfang</li>
<li>Hauptdiagnose</li>
<li>Therapieziele</li>
</ul>

<p><strong>VERLAUF UND ERGEBNISSE</strong></p>
<ul>
<li>Wichtige Fortschritte</li>
<li>Erreichte Ziele</li>
<li>Aktuelle Situation</li>
</ul>

<p><strong>FAZIT</strong></p>
<ul>
<li>Zusammenfassung</li>
<li>Empfehlungen</li>
</ul>''',
                    'max_tokens': 2000,
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