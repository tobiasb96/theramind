# Document Generation Prompts

# Centralized System Prompt for Document Generation
DOCUMENT_SYSTEM_PROMPT = """Du bist ein erfahrener Psychotherapeut und Assistent für Psychotherapeuten. 

WICHTIGE RICHTLINIEN FÜR DOKUMENTENERSTELLUNG:
1. **KEINE ERFINDUNGEN**: Erfinde niemals Informationen, die nicht in den bereitgestellten Sitzungsdaten enthalten sind. 
Wenn zu einem Thema keine Informationen vorhanden sind, schreibe "Keine Informationen verfügbar" 
oder lasse es weg.

2. **DATENSCHUTZ**: 
   - Verwende niemals echte Namen, Adressen, Geburtsdaten oder andere persönliche Daten
   - Ersetze Namen durch neutrale Bezeichnungen wie "der Patient", "die Patientin" oder Abkürzungen wie "K."
   - Verwende neutrale, professionelle Sprache

3. **NEUTRALE SPRACHE**: Beschreibe Patienten immer neutral und respektvoll als "der Patient" 
  oder "die Patientin", nicht mit Namen oder persönlichen Details.

4. **PROFESSIONALITÄT**: Erstelle strukturierte, professionelle Dokumente, die für medizinische 
  und therapeutische Zwecke geeignet sind.

5. **GENAUIGKEIT**: Beruhe ausschließlich auf den bereitgestellten Sitzungsdaten und mache keine Annahmen.

6. **STRUKTURIERTE DOKUMENTE**: Erstelle klar strukturierte, medizinisch fundierte Dokumente 
  mit entsprechenden Überschriften und Abschnitten."""

# Document type prompts
DOCUMENT_PROMPTS = {
    "abschlussbericht": {
        "name": "Abschlussbericht",
        "prompt": """Erstelle einen professionellen Abschlussbericht für eine Psychotherapie.

**PATIENTENINFORMATIONEN**
- Alter: {patient_info[age]}
- Geschlecht: {patient_info[gender]}
- Beruf: {patient_info[occupation]}
- Familienstand: {patient_info[marital_status]}

**THERAPIEINFORMATIONEN**
- Therapiebeginn: {therapy_info[start_date]}
- Therapieende: {therapy_info[end_date]}
- Anzahl Sitzungen: {therapy_info[session_count]}
- Therapieziele: {therapy_info[goals]}

**THERAPIEVERLAUF**
{transcriptions}

**ABSCHLUSSBERICHT**

1. **EINLEITUNG**
   - Kurze Darstellung der Ausgangssituation
   - Anlass der Therapie

2. **DIAGNOSTISCHE EINSCHÄTZUNG**
   - Hauptdiagnose
   - Differentialdiagnosen
   - Psychosoziale Faktoren

3. **THERAPIEVERLAUF**
   - Wichtige Stationen der Therapie
   - Bearbeitete Themen
   - Krisen und deren Bewältigung

4. **ERREICHTE ZIELE**
   - Positive Veränderungen
   - Erreichte Therapieziele
   - Neue Bewältigungsstrategien

5. **AKTUELLER STATUS**
   - Aktuelle Symptomatik
   - Psychosoziale Situation
   - Bewältigungsfähigkeiten

6. **PROGNOSE UND EMPFEHLUNGEN**
   - Einschätzung der weiteren Entwicklung
   - Empfehlungen für die Zukunft
   - Nachsorgeplan

7. **ABSCHLUSS**
   - Zusammenfassung der Therapie
   - Dank an den Patienten für die Zusammenarbeit

Der Bericht sollte professionell, strukturiert und für medizinische Zwecke geeignet sein.""",
    },
    
    "verlaufsbericht": {
        "name": "Verlaufsbericht",
        "prompt": """Erstelle einen Verlaufsbericht für eine laufende Psychotherapie.

**PATIENTENINFORMATIONEN**
- Alter: {patient_info[age]}
- Geschlecht: {patient_info[gender]}
- Beruf: {patient_info[occupation]}
- Familienstand: {patient_info[marital_status]}

**THERAPIEINFORMATIONEN**
- Therapiebeginn: {therapy_info[start_date]}
- Aktueller Status: {therapy_info[status]}
- Anzahl Sitzungen: {therapy_info[session_count]}
- Therapieziele: {therapy_info[goals]}

**THERAPIEVERLAUF**
{transcriptions}

**VERLAUFSBERICHT**

1. **AKTUELLE SITUATION**
   - Aktuelle Beschwerden und Symptome
   - Psychosoziale Situation
   - Belastungsfaktoren

2. **THERAPIEVERLAUF BISLANG**
   - Wichtige Stationen der Therapie
   - Bearbeitete Themen
   - Erreichte Fortschritte

3. **AKTUELLE SITZUNGEN**
   - Fokus der letzten Sitzungen
   - Neue Erkenntnisse
   - Schwierigkeiten und Rückschläge

4. **FORTSCHRITT UND VERÄNDERUNGEN**
   - Positive Entwicklungen
   - Verbleibende Herausforderungen
   - Neue Bewältigungsstrategien

5. **NÄCHSTE SCHRITTE**
   - Geplante Interventionen
   - Fokus für kommende Sitzungen
   - Ziele für die nächste Phase

6. **PROGNOSE**
   - Einschätzung der weiteren Entwicklung
   - Erwartete Dauer der Therapie

Der Bericht sollte den aktuellen Stand der Therapie widerspiegeln und für die weitere Behandlung relevant sein.""",
    },
    
    "befundbericht": {
        "name": "Befundbericht",
        "prompt": """Erstelle einen Befundbericht für eine psychotherapeutische Untersuchung.

**PATIENTENINFORMATIONEN**
- Alter: {patient_info[age]}
- Geschlecht: {patient_info[gender]}
- Beruf: {patient_info[occupation]}
- Familienstand: {patient_info[marital_status]}

**THERAPIEINFORMATIONEN**
- Therapiebeginn: {therapy_info[start_date]}
- Anzahl Sitzungen: {therapy_info[session_count]}

**SITZUNGSDATEN**
{transcriptions}

**BEFUNDBERICHT**

1. **ANAMNESE**
   - Aktuelle Beschwerden
   - Psychiatrische Vorgeschichte
   - Somatische Vorgeschichte
   - Familienanamnese
   - Sozialanamnese

2. **PSYCHISCHER BEFUND**
   - Bewusstsein und Orientierung
   - Stimmung und Affekt
   - Denken und Wahrnehmung
   - Antrieb und Psychomotorik
   - Kognitive Funktionen

3. **DIAGNOSTISCHE EINSCHÄTZUNG**
   - Hauptdiagnose nach ICD-10
   - Differentialdiagnosen
   - Schweregrad
   - Psychosoziale Faktoren

4. **THERAPIEEMPFEHLUNG**
   - Indikation für Psychotherapie
   - Empfohlene Therapieform
   - Therapieziele
   - Erwartete Dauer

5. **PROGNOSE**
   - Einschätzung der Behandelbarkeit
   - Erwartete Entwicklung
   - Risikofaktoren

Der Befundbericht sollte medizinisch fundiert und für weitere Behandler verständlich sein.""",
    },
    
    "indikationsstellung": {
        "name": "Indikationsstellung",
        "prompt": """Erstelle eine Indikationsstellung für eine Psychotherapie.

**PATIENTENINFORMATIONEN**
- Alter: {patient_info[age]}
- Geschlecht: {patient_info[gender]}
- Beruf: {patient_info[occupation]}
- Familienstand: {patient_info[marital_status]}

**THERAPIEINFORMATIONEN**
- Therapiebeginn: {therapy_info[start_date]}
- Anzahl Sitzungen: {therapy_info[session_count]}

**SITZUNGSDATEN**
{transcriptions}

**INDIKATIONSSTELLUNG**

1. **AKTUELLE PROBLEMATIK**
   - Hauptbeschwerden
   - Symptomatik
   - Leidensdruck
   - Funktionsbeeinträchtigung

2. **DIAGNOSTISCHE EINSCHÄTZUNG**
   - Verdachtsdiagnose
   - Differentialdiagnosen
   - Komorbiditäten
   - Psychosoziale Faktoren

3. **INDIKATION FÜR PSYCHOTHERAPIE**
   - Begründung der Indikation
   - Ausschlusskriterien
   - Kontraindikationen
   - Risiko-Nutzen-Abwägung

4. **THERAPIEEMPFEHLUNG**
   - Empfohlene Therapieform
   - Begründung der Wahl
   - Alternative Behandlungsoptionen
   - Setting-Empfehlung

5. **THERAPIEZIELE**
   - Primäre Ziele
   - Sekundäre Ziele
   - Realistische Erwartungen
   - Erfolgskriterien

6. **PROGNOSE**
   - Behandelbarkeit
   - Erwartete Dauer
   - Erfolgsaussichten
   - Risikofaktoren

Die Indikationsstellung sollte medizinisch begründet und für Kostenträger nachvollziehbar sein.""",
    },
    
    "anamnese": {
        "name": "Anamnese",
        "prompt": """Erstelle eine strukturierte Anamnese für eine psychotherapeutische Behandlung.

**PATIENTENINFORMATIONEN**
- Alter: {patient_info[age]}
- Geschlecht: {patient_info[gender]}
- Beruf: {patient_info[occupation]}
- Familienstand: {patient_info[marital_status]}

**SITZUNGSDATEN**
{transcriptions}

**ANAMNESE**

1. **AKTUELLE BESCHWERDEN**
   - Hauptbeschwerden
   - Beginn und Verlauf
   - Auslöser und aufrechterhaltende Faktoren
   - Schweregrad und Beeinträchtigung

2. **PSYCHIATRISCHE VORGESCHICHTE**
   - Frühere psychische Erkrankungen
   - Vorbehandlungen
   - Medikamentöse Behandlungen
   - Stationäre Aufenthalte

3. **SOMATISCHE VORGESCHICHTE**
   - Relevante körperliche Erkrankungen
   - Operationen
   - Medikamente
   - Allergien

4. **FAMILIENANAMNESE**
   - Psychische Erkrankungen in der Familie
   - Genetische Belastungen
   - Familiäre Konflikte
   - Unterstützende Faktoren

5. **SOZIALANAMNESE**
   - Familienverhältnisse
   - Partnerschaft
   - Berufliche Situation
   - Soziale Kontakte
   - Finanzielle Situation

6. **ENTWICKLUNGSANAMNESE**
   - Schwangerschaft und Geburt
   - Frühe Entwicklung
   - Schulische Entwicklung
   - Berufliche Entwicklung
   - Lebenskrisen

7. **PERSÖNLICHKEITSANAMNESE**
   - Charaktereigenschaften
   - Bewältigungsstrategien
   - Stärken und Ressourcen
   - Schwächen und Vulnerabilitäten

Die Anamnese sollte umfassend und für die Therapieplanung relevant sein.""",
    },
    
    "diagnose": {
        "name": "Diagnose",
        "prompt": """Erstelle eine differenzierte Diagnose für eine psychotherapeutische Behandlung.

**PATIENTENINFORMATIONEN**
- Alter: {patient_info[age]}
- Geschlecht: {patient_info[gender]}
- Beruf: {patient_info[occupation]}
- Familienstand: {patient_info[marital_status]}

**SITZUNGSDATEN**
{transcriptions}

**DIAGNOSE**

1. **HAUPTDIAGNOSE**
   - ICD-10 Diagnose
   - Schweregrad
   - Verlaufstyp
   - Begründung der Diagnose

2. **DIFFERENTIALDIAGNOSEN**
   - Abzugrenzende Störungen
   - Ausschlusskriterien
   - Komorbiditäten
   - Differentialdiagnostische Überlegungen

3. **PSYCHOSOZIALE FAKTOREN**
   - Belastende Lebensereignisse
   - Aktuelle Belastungen
   - Soziale Unterstützung
   - Bewältigungsressourcen

4. **FUNKTIONSBEEINTRÄCHTIGUNG**
   - Berufliche Beeinträchtigung
   - Soziale Beeinträchtigung
   - Familiäre Beeinträchtigung
   - Grad der Beeinträchtigung

5. **RISIKOFAKTOREN**
   - Suizidalität
   - Selbstgefährdung
   - Fremdgefährdung
   - Suchtgefährdung

6. **PROTECTIVE FAKTOREN**
   - Soziale Unterstützung
   - Bewältigungsstrategien
   - Motivation zur Behandlung
   - Ressourcen

Die Diagnose sollte fundiert und für die Therapieplanung relevant sein.""",
    },
    
    "therapieplan": {
        "name": "Therapieplan",
        "prompt": """Erstelle einen strukturierten Therapieplan für eine psychotherapeutische Behandlung.

**PATIENTENINFORMATIONEN**
- Alter: {patient_info[age]}
- Geschlecht: {patient_info[gender]}
- Beruf: {patient_info[occupation]}
- Familienstand: {patient_info[marital_status]}

**THERAPIEINFORMATIONEN**
- Therapiebeginn: {therapy_info[start_date]}
- Anzahl Sitzungen: {therapy_info[session_count]}
- Therapieziele: {therapy_info[goals]}

**SITZUNGSDATEN**
{transcriptions}

**THERAPIEPLAN**

1. **DIAGNOSE UND INDIKATION**
   - Hauptdiagnose
   - Indikation für Psychotherapie
   - Ausschlusskriterien
   - Kontraindikationen

2. **THERAPIEZIELE**
   - Primäre Ziele
   - Sekundäre Ziele
   - Kurzzeitziele
   - Langzeitziele
   - Erfolgskriterien

3. **THERAPIEMETHODE**
   - Gewählte Therapieform
   - Begründung der Wahl
   - Spezifische Techniken
   - Anpassungen an den Patienten

4. **THERAPIEVERLAUF**
   - Phase 1: Aufbau und Stabilisierung
   - Phase 2: Bearbeitung der Probleme
   - Phase 3: Konsolidierung und Abschluss
   - Übergänge zwischen Phasen

5. **INTERVENTIONEN**
   - Spezifische Interventionen
   - Hausaufgaben und Übungen
   - Kriseninterventionen
   - Rückfallprophylaxe

6. **EVALUATION**
   - Erfolgskontrolle
   - Messinstrumente
   - Zeitpunkte der Evaluation
   - Anpassung des Plans

7. **ABSCHLUSSKRITERIEN**
   - Kriterien für Therapieende
   - Nachsorgeplan
   - Rückfallprophylaxe
   - Wiedereinstiegskriterien

Der Therapieplan sollte strukturiert und für die Behandlung leitend sein.""",
    },
    
    "brief": {
        "name": "Brief",
        "prompt": """Erstelle einen professionellen Brief für einen Patienten oder andere Behandler.

**PATIENTENINFORMATIONEN**
- Alter: {patient_info[age]}
- Geschlecht: {patient_info[gender]}
- Beruf: {patient_info[occupation]}
- Familienstand: {patient_info[marital_status]}

**THERAPIEINFORMATIONEN**
- Therapiebeginn: {therapy_info[start_date]}
- Anzahl Sitzungen: {therapy_info[session_count]}

**SITZUNGSDATEN**
{transcriptions}

**BRIEF**

1. **ANREDE UND EINLEITUNG**
   - Professionelle Anrede
   - Bezug auf vorherige Kontakte
   - Anlass des Briefes

2. **AKTUELLE SITUATION**
   - Zusammenfassung der aktuellen Situation
   - Wichtige Entwicklungen
   - Aktuelle Beschwerden

3. **THERAPIEVERLAUF**
   - Wichtige Stationen der Behandlung
   - Erreichte Fortschritte
   - Verbleibende Herausforderungen

4. **EMPFEHLUNGEN**
   - Konkrete Empfehlungen
   - Weitere Schritte
   - Kooperation mit anderen Behandlern

5. **ABSCHLUSS**
   - Zusammenfassung
   - Dank und Wertschätzung
   - Professionelle Grußformel

Der Brief sollte professionell, respektvoll und für den Empfänger verständlich sein.""",
    },
    
    "other": {
        "name": "Sonstiges",
        "prompt": """Erstelle ein allgemeines Dokument für eine psychotherapeutische Behandlung.

**PATIENTENINFORMATIONEN**
- Alter: {patient_info[age]}
- Geschlecht: {patient_info[gender]}
- Beruf: {patient_info[occupation]}
- Familienstand: {patient_info[marital_status]}

**THERAPIEINFORMATIONEN**
- Therapiebeginn: {therapy_info[start_date]}
- Anzahl Sitzungen: {therapy_info[session_count]}

**SITZUNGSDATEN**
{transcriptions}

**DOKUMENT**

Erstelle ein strukturiertes, professionelles Dokument, das die wichtigsten Informationen zur Behandlung zusammenfasst. Das Dokument sollte enthalten:

1. **PATIENTENINFORMATIONEN**
   - Relevante biografische Daten
   - Aktuelle Situation

2. **THERAPIEINFORMATIONEN**
   - Therapieverlauf
   - Wichtige Entwicklungen
   - Erreichte Fortschritte

3. **FAZIT UND EMPFEHLUNGEN**
   - Zusammenfassung
   - Empfehlungen für die Zukunft

Das Dokument sollte professionell und für medizinische Zwecke geeignet sein.""",
    },
}

def get_document_prompt(document_type: str) -> str:
    """Get the prompt for a specific document type."""
    if document_type not in DOCUMENT_PROMPTS:
        raise ValueError(f"Unknown document type: {document_type}")
    return DOCUMENT_PROMPTS[document_type]["prompt"]

def get_available_document_types() -> dict:
    """Get all available document types."""
    return {key: template["name"] for key, template in DOCUMENT_PROMPTS.items()} 