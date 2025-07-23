
report_initial = """
<p><strong>Anlass der Vorstellung</strong></p>
<ul>
<li>Grund der Kontaktaufnahme und Überweisung</li>
<li>Aktuelle Beschwerdesymptomatik</li>
</ul>

<p><strong>Anamnese</strong></p>
<ul>
<li>Eigenanamnese mit aktueller Symptomatik</li>
<li>Biografische Anamnese und relevante Lebensereignisse</li>
<li>Familienanamnese und psychosoziale Faktoren</li>
<li>Medizinische Anamnese und aktuelle Medikation</li>
</ul>

<p><strong>Psychopathologischer Befund</strong></p>
<ul>
<li>Aktueller psychischer Befund nach AMDP-System</li>
<li>Bewusstsein, Orientierung, Aufmerksamkeit</li>
<li>Affektivität, Antrieb, Psychomotorik</li>
<li>Denkstörungen, Wahrnehmungsstörungen</li>
</ul>

<p><strong>Diagnose</strong></p>
<ul>
<li>Hauptdiagnose nach ICD-10</li>
<li>Nebendiagnosen</li>
<li>Differentialdiagnosen</li>
<li>Ausschlussdiagnosen</li>
</ul>

<p><strong>Krankheitsverlauf und Prognose</strong></p>
<ul>
<li>Bisheriger Verlauf der Erkrankung</li>
<li>Prognostische Einschätzung</li>
<li>Risiko- und Schutzfaktoren</li>
</ul>

<p><strong>Behandlungsplan</strong></p>
<ul>
<li>Empfohlenes Therapieverfahren</li>
<li>Therapieziele und -schwerpunkte</li>
<li>Geplante Therapiedauer und -frequenz</li>
<li>Zusätzliche Maßnahmen</li>
</ul>

<p><strong>Zusammenfassung und Empfehlung</strong></p>
<ul>
<li>Kurze Zusammenfassung des Falls</li>
<li>Behandlungsnotwendigkeit und -dringlichkeit</li>
<li>Empfehlung für Kostenübernahme</li>
</ul>
"""

report_initial_general_instructions = """
"""

report_conversion = """
"""

report_conversion_general_instructions = """
"""

report_psychological_findings = """
<p><strong>Anlass der Untersuchung</strong></p>
<ul>
<li>Fragestellung und Auftrag</li>
<li>Überweisender Arzt/Institution</li>
<li>Untersuchungsdatum und -rahmen</li>
</ul>

<p><strong>Anamnese</strong></p>
<ul>
<li>Aktuelle Beschwerden und Symptomatik</li>
<li>Krankheitsverlauf und Vorbehandlungen</li>
<li>Biografische Anamnese</li>
<li>Familienanamnese</li>
<li>Soziale und berufliche Situation</li>
</ul>

<p><strong>Verhaltensbeobachtung</strong></p>
<ul>
<li>Äußere Erscheinung und Verhalten</li>
<li>Kontaktverhalten und Kooperationsbereitschaft</li>
<li>Psychomotorische Auffälligkeiten</li>
<li>Besonderheiten während der Untersuchung</li>
</ul>

<p><strong>Psychopathologischer Befund</strong></p>
<ul>
<li>Bewusstsein und Orientierung</li>
<li>Aufmerksamkeit und Konzentration</li>
<li>Gedächtnis und kognitive Funktionen</li>
<li>Denkstörungen und Denkinhalt</li>
<li>Wahrnehmung und Sinnestäuschungen</li>
<li>Affektivität und Stimmung</li>
<li>Antrieb und Psychomotorik</li>
<li>Ich-Störungen</li>
</ul>

<p><strong>Testpsychologische Untersuchung</strong></p>
<ul>
<li>Verwendete Testverfahren</li>
<li>Testergebnisse und Interpretation</li>
<li>Leistungsprofil und Auffälligkeiten</li>
</ul>

<p><strong>Diagnostische Einschätzung</strong></p>
<ul>
<li>Diagnose nach ICD-10</li>
<li>Differentialdiagnosen</li>
<li>Schweregrad und Verlauf</li>
<li>Komorbidität</li>
</ul>

<p><strong>Zusammenfassung und Empfehlungen</strong></p>
<ul>
<li>Zusammenfassende Beurteilung</li>
<li>Behandlungsempfehlungen</li>
<li>Prognostische Einschätzung</li>
<li>Weitere diagnostische Schritte</li>
</ul>
"""

report_psychological_findings_general_instructions = """
"""

report_doctors_letter = """
"""

report_doctors_letter_general_instructions = """
"""

report_epicrisis = """
"""

report_epicrisis_general_instructions = """
"""

REPORT_TEMPLATES = {
    "initial_report": report_initial,
    "conversion_report": report_conversion,
    "psychological_findings_report": report_psychological_findings,
    "doctors_letter_report": report_doctors_letter,
    "epicrisis_report": report_epicrisis,
}

REPORT_GENERAL_INSTRUCTIONS = {
    "initial_report": report_initial_general_instructions,
    "conversion_report": report_conversion_general_instructions,
    "psychological_findings_report": report_psychological_findings_general_instructions,
    "doctors_letter_report": report_doctors_letter_general_instructions,
    "epicrisis_report": report_epicrisis_general_instructions,
}