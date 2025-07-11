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

5. **GENAUIGKEIT**: Beruhe ausschließlich auf den bereitgestellten Informationen und mache keine Annahmen."""

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

Strukturierte Notizen:""",
    },
    "verlaufsgespraech": {
        "name": "Verlaufsgespräch",
        "prompt": """Erstelle strukturierte Sitzungsnotizen für ein Verlaufsgespräch basierend auf dem Transkript.

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

Strukturierte Notizen:""",
    },
    "abschlussgespraech": {
        "name": "Abschlussgespräch",
        "prompt": """Erstelle strukturierte Sitzungsnotizen für ein Abschlussgespräch basierend auf dem Transkript.

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
