# Centralized System Prompt for Privacy and Accuracy
SYSTEM_PROMPT = """Du bist ein erfahrener Psychotherapeut und Assistent für Psychotherapeuten. 

WICHTIGE RICHTLINIEN:
1. **KEINE ERFINDUNGEN**: Erfinde niemals Informationen, die nicht im bereitgestellten Text enthalten sind. 
Wenn zu einem Thema keine Informationen vorhanden sind, schreibe "Keine Informationen verfügbar" 
oder lasse es weg.

2. **DATENSCHUTZ**: 
   - Verwende niemals echte Namen, Adressen, Geburtsdaten oder andere persönliche Daten
   - Ersetze Namen durch neutrale Bezeichnungen wie "der Patient", "die Patientin" oder Abkürzungen wie "K."
   - Verwende neutrale, professionelle Sprache

3. **NEUTRALE SPRACHE**: Beschreibe Patienten immer neutral und respektvoll als "der Patient" 
  oder "die Patientin", nicht mit Namen oder persönlichen Details.

4. **PROFESSIONALITÄT**: Erstelle strukturierte, professionelle Notizen, die für therapeutische 
  Zwecke geeignet sind.

5. **GENAUIGKEIT**: Beruhe ausschließlich auf den bereitgestellten Informationen und mache keine Annahmen.

6. **HTML-FORMATIERUNG**: Antworte IMMER in HTML-Format mit folgenden erlaubten Tags:
   - <p> für Absätze
   - <strong> für fettgedruckten Text
   - <ul> für ungeordnete Listen
   - <ol> für geordnete Listen  
   - <li> für Listenelemente
   
   Verwende KEINE anderen HTML-Tags. Strukturiere den Inhalt klar mit Absätzen und Listen."""

# Summary prompt - ultra-short summary for display at top
SUMMARY_PROMPT = """Erstelle eine ultra-kurze Zusammenfassung (max. 50 Wörter) einer Therapiesitzung.

Die Zusammenfassung sollte enthalten:
- Art der Sitzung (z.B. Erstgespräch, Verlaufsgespräch, Abschlussgespräch)
- Hauptthema/Themen
- Wichtigste Erkenntnisse oder Fortschritte

Fasse folgende Therapiesitzung zusammen:

{transcript}

Zusammenfassung:"""

# Session Notes Templates
SESSION_NOTES_TEMPLATES = {
    "erstgespraech": {
        "name": "Erstgespräch",
        "prompt": """Erstelle strukturierte Sitzungsnotizen für ein Erstgespräch basierend auf dem Transkript.

Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

Strukturiere die Notizen wie folgt:

<p><strong>ANAMNESE</strong></p>
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
</ul>

Transkript der Sitzung:
{transcript}

Strukturierte Notizen:""",
    },
    "verlaufsgespraech": {
        "name": "Verlaufsgespräch",
        "prompt": """Erstelle strukturierte Sitzungsnotizen für ein Verlaufsgespräch basierend auf dem Transkript.

Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

Strukturiere die Notizen wie folgt:

<p><strong>VERLAUF SEIT LETZTER SITZUNG</strong></p>
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
</ul>

Transkript der Sitzung:
{transcript}

Strukturierte Notizen:""",
    },
    "abschlussgespraech": {
        "name": "Abschlussgespräch",
        "prompt": """Erstelle strukturierte Sitzungsnotizen für ein Abschlussgespräch basierend auf dem Transkript.

Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

Strukturiere die Notizen wie folgt:

<p><strong>THERAPIEFORTSCHRITT</strong></p>
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
</ul>

Transkript der Sitzung:
{transcript}

Strukturierte Notizen:""",
    },
}

def get_session_notes_prompt(template_key: str) -> str:
    """Get the prompt for a specific session notes template."""
    if template_key not in SESSION_NOTES_TEMPLATES:
        raise ValueError(f"Unknown template: {template_key}")
    return SESSION_NOTES_TEMPLATES[template_key]["prompt"]

def get_available_templates() -> dict:
    """Get all available session notes templates."""
    return {key: template["name"] for key, template in SESSION_NOTES_TEMPLATES.items()}
