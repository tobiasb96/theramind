# AI Prompts for Therapy Session Processing

# Summary prompt - ultra-short summary for display at top
SUMMARY_PROMPT = """Du bist ein Assistent für Psychotherapeuten. Erstelle eine ultra-kurze Zusammenfassung (max. 50 Wörter) einer Therapiesitzung.

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
        "prompt": """Du bist ein erfahrener Psychotherapeut. Erstelle strukturierte Sitzungsnotizen für ein Erstgespräch basierend auf dem Transkript.

Strukturiere die Notizen wie folgt:

**ANAMNESE**
- Aktuelle Beschwerden und Symptome
- Psychosoziale Situation
- Biografische Informationen
- Vorbehandlungen

**DIAGNOSTISCHE EINSCHÄTZUNG**
- Erste Eindrücke
- Mögliche Diagnosen
- Risikofaktoren

**THERAPIEZIELE**
- Hauptziele des Patienten
- Behandlungsansatz

**NÄCHSTE SCHRITTE**
- Empfohlene Maßnahmen
- Terminvereinbarung

Transkript der Sitzung:
{transcript}

Strukturierte Notizen:"""
    },
    
    "verlaufsgespraech": {
        "name": "Verlaufsgespräch", 
        "prompt": """Du bist ein erfahrener Psychotherapeut. Erstelle strukturierte Sitzungsnotizen für ein Verlaufsgespräch basierend auf dem Transkript.

Strukturiere die Notizen wie folgt:

**VERLAUF SEIT LETZTER SITZUNG**
- Veränderungen und Fortschritte
- Schwierigkeiten und Rückschläge
- Compliance mit Übungen/Aufgaben

**AKTUELLE SITZUNG**
- Hauptthemen und Inhalte
- Neue Erkenntnisse
- Bearbeitete Problembereiche

**FORTSCHRITT UND VERÄNDERUNGEN**
- Positive Entwicklungen
- Verbleibende Herausforderungen
- Erreichte Ziele

**NÄCHSTE SCHRITTE**
- Neue Aufgaben/Übungen
- Fokus für nächste Sitzung
- Terminvereinbarung

Transkript der Sitzung:
{transcript}

Strukturierte Notizen:"""
    },
    
    "abschlussgespraech": {
        "name": "Abschlussgespräch",
        "prompt": """Du bist ein erfahrener Psychotherapeut. Erstelle strukturierte Sitzungsnotizen für ein Abschlussgespräch basierend auf dem Transkript.

Strukturiere die Notizen wie folgt:

**THERAPIEFORTSCHRITT**
- Erreichte Ziele
- Positive Veränderungen
- Gelernte Strategien

**AKTUELLER STATUS**
- Aktuelle Symptomatik
- Bewältigungsfähigkeiten
- Psychosoziale Situation

**RÜCKFALLPROPHYLAXE**
- Risikofaktoren
- Frühwarnzeichen
- Bewältigungsstrategien

**ABSCHLUSS**
- Zusammenfassung der Therapie
- Empfehlungen für die Zukunft
- Nachsorgeplan

Transkript der Sitzung:
{transcript}

Strukturierte Notizen:"""
    }
}

def get_session_notes_prompt(template_key: str) -> str:
    """Get the prompt for a specific session notes template."""
    if template_key not in SESSION_NOTES_TEMPLATES:
        raise ValueError(f"Unknown template: {template_key}")
    return SESSION_NOTES_TEMPLATES[template_key]["prompt"]

def get_available_templates() -> dict:
    """Get all available session notes templates."""
    return {key: template["name"] for key, template in SESSION_NOTES_TEMPLATES.items()}
