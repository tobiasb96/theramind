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
  mit entsprechenden Überschriften und Abschnitten.

7. **HTML-FORMATIERUNG**: Antworte IMMER in HTML-Format mit folgenden erlaubten Tags:
   - <p> für Absätze
   - <strong> für fettgedruckten Text
   - <ul> für ungeordnete Listen
   - <ol> für geordnete Listen  
   - <li> für Listenelemente
   
   Verwende KEINE anderen HTML-Tags. Strukturiere den Inhalt klar mit Absätzen und Listen."""

# Document type prompts
DOCUMENT_PROMPTS = {
    "abschlussbericht": {
        "name": "Abschlussbericht",
        "prompt": """Erstelle einen professionellen Abschlussbericht für eine Psychotherapie.

Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

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

<p><strong>1. EINLEITUNG</strong></p>
<ul>
<li>Kurze Darstellung der Ausgangssituation</li>
<li>Anlass der Therapie</li>
</ul>

<p><strong>2. DIAGNOSTISCHE EINSCHÄTZUNG</strong></p>
<ul>
<li>Hauptdiagnose</li>
<li>Differentialdiagnosen</li>
<li>Psychosoziale Faktoren</li>
</ul>

<p><strong>3. THERAPIEVERLAUF</strong></p>
<ul>
<li>Wichtige Stationen der Therapie</li>
<li>Bearbeitete Themen</li>
<li>Krisen und deren Bewältigung</li>
</ul>

<p><strong>4. ERREICHTE ZIELE</strong></p>
<ul>
<li>Positive Veränderungen</li>
<li>Erreichte Therapieziele</li>
<li>Neue Bewältigungsstrategien</li>
</ul>

<p><strong>5. AKTUELLER STATUS</strong></p>
<ul>
<li>Aktuelle Symptomatik</li>
<li>Psychosoziale Situation</li>
<li>Bewältigungsfähigkeiten</li>
</ul>

<p><strong>6. PROGNOSE UND EMPFEHLUNGEN</strong></p>
<ul>
<li>Einschätzung der weiteren Entwicklung</li>
<li>Empfehlungen für die Zukunft</li>
<li>Nachsorgeplan</li>
</ul>

<p><strong>7. ABSCHLUSS</strong></p>
<ul>
<li>Zusammenfassung der Therapie</li>
<li>Dank an den Patienten für die Zusammenarbeit</li>
</ul>

Der Bericht sollte professionell, strukturiert und für medizinische Zwecke geeignet sein.""",
    },
    "verlaufsbericht": {
        "name": "Verlaufsbericht",
        "prompt": """Erstelle einen Verlaufsbericht für eine laufende Psychotherapie.

Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

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

<p><strong>1. AKTUELLE SITUATION</strong></p>
<ul>
<li>Aktuelle Beschwerden und Symptome</li>
<li>Psychosoziale Situation</li>
<li>Belastungsfaktoren</li>
</ul>

<p><strong>2. THERAPIEVERLAUF BISLANG</strong></p>
<ul>
<li>Wichtige Stationen der Therapie</li>
<li>Bearbeitete Themen</li>
<li>Erreichte Fortschritte</li>
</ul>

<p><strong>3. AKTUELLE SITZUNGEN</strong></p>
<ul>
<li>Fokus der letzten Sitzungen</li>
<li>Neue Erkenntnisse</li>
<li>Schwierigkeiten und Rückschläge</li>
</ul>

<p><strong>4. FORTSCHRITT UND VERÄNDERUNGEN</strong></p>
<ul>
<li>Positive Entwicklungen</li>
<li>Verbleibende Herausforderungen</li>
<li>Neue Bewältigungsstrategien</li>
</ul>

<p><strong>5. NÄCHSTE SCHRITTE</strong></p>
<ul>
<li>Geplante Interventionen</li>
<li>Fokus für kommende Sitzungen</li>
<li>Ziele für die nächste Phase</li>
</ul>

<p><strong>6. PROGNOSE</strong></p>
<ul>
<li>Einschätzung der weiteren Entwicklung</li>
<li>Erwartete Dauer der Therapie</li>
</ul>

Der Bericht sollte den aktuellen Stand der Therapie widerspiegeln und für die weitere Behandlung relevant sein.""",
    },
    "befundbericht": {
        "name": "Befundbericht",
        "prompt": """Erstelle einen Befundbericht für eine psychotherapeutische Untersuchung.

Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

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

<p><strong>1. ANAMNESE</strong></p>
<ul>
<li>Aktuelle Beschwerden</li>
<li>Psychiatrische Vorgeschichte</li>
<li>Somatische Vorgeschichte</li>
<li>Familienanamnese</li>
<li>Sozialanamnese</li>
</ul>

<p><strong>2. PSYCHISCHER BEFUND</strong></p>
<ul>
<li>Bewusstsein und Orientierung</li>
<li>Stimmung und Affekt</li>
<li>Denken und Wahrnehmung</li>
<li>Antrieb und Psychomotorik</li>
<li>Kognitive Funktionen</li>
</ul>

<p><strong>3. DIAGNOSTISCHE EINSCHÄTZUNG</strong></p>
<ul>
<li>Hauptdiagnose nach ICD-10</li>
<li>Differentialdiagnosen</li>
<li>Schweregrad</li>
<li>Psychosoziale Faktoren</li>
</ul>

<p><strong>4. THERAPIEEMPFEHLUNG</strong></p>
<ul>
<li>Indikation für Psychotherapie</li>
<li>Empfohlene Therapieform</li>
<li>Therapieziele</li>
<li>Erwartete Dauer</li>
</ul>

<p><strong>5. PROGNOSE</strong></p>
<ul>
<li>Einschätzung der Behandelbarkeit</li>
<li>Erwartete Entwicklung</li>
<li>Risikofaktoren</li>
</ul>

Der Befundbericht sollte medizinisch fundiert und für weitere Behandler verständlich sein.""",
    },
    "indikationsstellung": {
        "name": "Indikationsstellung",
        "prompt": """Erstelle eine Indikationsstellung für eine Psychotherapie.

Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

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

<p><strong>1. AKTUELLE PROBLEMATIK</strong></p>
<ul>
<li>Hauptbeschwerden</li>
<li>Symptomatik</li>
<li>Leidensdruck</li>
<li>Funktionsbeeinträchtigung</li>
</ul>

<p><strong>2. DIAGNOSTISCHE EINSCHÄTZUNG</strong></p>
<ul>
<li>Verdachtsdiagnose</li>
<li>Differentialdiagnosen</li>
<li>Komorbiditäten</li>
<li>Psychosoziale Faktoren</li>
</ul>

<p><strong>3. INDIKATION FÜR PSYCHOTHERAPIE</strong></p>
<ul>
<li>Begründung der Indikation</li>
<li>Ausschlusskriterien</li>
<li>Kontraindikationen</li>
<li>Risiko-Nutzen-Abwägung</li>
</ul>

<p><strong>4. THERAPIEEMPFEHLUNG</strong></p>
<ul>
<li>Empfohlene Therapieform</li>
<li>Begründung der Wahl</li>
<li>Alternative Behandlungsoptionen</li>
<li>Setting-Empfehlung</li>
</ul>

<p><strong>5. THERAPIEZIELE</strong></p>
<ul>
<li>Primäre Ziele</li>
<li>Sekundäre Ziele</li>
<li>Realistische Erwartungen</li>
<li>Erfolgskriterien</li>
</ul>

<p><strong>6. PROGNOSE</strong></p>
<ul>
<li>Behandelbarkeit</li>
<li>Erwartete Dauer</li>
<li>Erfolgsaussichten</li>
<li>Risikofaktoren</li>
</ul>

Die Indikationsstellung sollte medizinisch begründet und für Kostenträger nachvollziehbar sein.""",
    },
    "anamnese": {
        "name": "Anamnese",
        "prompt": """Erstelle eine strukturierte Anamnese für eine psychotherapeutische Behandlung.

Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

**PATIENTENINFORMATIONEN**
- Alter: {patient_info[age]}
- Geschlecht: {patient_info[gender]}
- Beruf: {patient_info[occupation]}
- Familienstand: {patient_info[marital_status]}

**SITZUNGSDATEN**
{transcriptions}

**ANAMNESE**

<p><strong>1. AKTUELLE BESCHWERDEN</strong></p>
<ul>
<li>Hauptbeschwerden</li>
<li>Beginn und Verlauf</li>
<li>Auslöser und aufrechterhaltende Faktoren</li>
<li>Schweregrad und Beeinträchtigung</li>
</ul>

<p><strong>2. PSYCHIATRISCHE VORGESCHICHTE</strong></p>
<ul>
<li>Frühere psychische Erkrankungen</li>
<li>Vorbehandlungen</li>
<li>Medikamentöse Behandlungen</li>
<li>Stationäre Aufenthalte</li>
</ul>

<p><strong>3. SOMATISCHE VORGESCHICHTE</strong></p>
<ul>
<li>Relevante körperliche Erkrankungen</li>
<li>Operationen</li>
<li>Medikamente</li>
<li>Allergien</li>
</ul>

<p><strong>4. FAMILIENANAMNESE</strong></p>
<ul>
<li>Psychische Erkrankungen in der Familie</li>
<li>Genetische Belastungen</li>
<li>Familiäre Konflikte</li>
<li>Unterstützende Faktoren</li>
</ul>

<p><strong>5. SOZIALANAMNESE</strong></p>
<ul>
<li>Familienverhältnisse</li>
<li>Partnerschaft</li>
<li>Berufliche Situation</li>
<li>Soziale Kontakte</li>
<li>Finanzielle Situation</li>
</ul>

<p><strong>6. ENTWICKLUNGSANAMNESE</strong></p>
<ul>
<li>Schwangerschaft und Geburt</li>
<li>Frühe Entwicklung</li>
<li>Schulische Entwicklung</li>
<li>Berufliche Entwicklung</li>
<li>Lebenskrisen</li>
</ul>

<p><strong>7. PERSÖNLICHKEITSANAMNESE</strong></p>
<ul>
<li>Charaktereigenschaften</li>
<li>Bewältigungsstrategien</li>
<li>Stärken und Ressourcen</li>
<li>Schwächen und Vulnerabilitäten</li>
</ul>

Die Anamnese sollte umfassend und für die Therapieplanung relevant sein.""",
    },
    "diagnose": {
        "name": "Diagnose",
        "prompt": """Erstelle eine differenzierte Diagnose für eine psychotherapeutische Behandlung.

Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

**PATIENTENINFORMATIONEN**
- Alter: {patient_info[age]}
- Geschlecht: {patient_info[gender]}
- Beruf: {patient_info[occupation]}
- Familienstand: {patient_info[marital_status]}

**SITZUNGSDATEN**
{transcriptions}

**DIAGNOSE**

<p><strong>1. HAUPTDIAGNOSE</strong></p>
<ul>
<li>ICD-10 Diagnose</li>
<li>Schweregrad</li>
<li>Verlaufstyp</li>
<li>Begründung der Diagnose</li>
</ul>

<p><strong>2. DIFFERENTIALDIAGNOSEN</strong></p>
<ul>
<li>Abzugrenzende Störungen</li>
<li>Ausschlusskriterien</li>
<li>Komorbiditäten</li>
<li>Differentialdiagnostische Überlegungen</li>
</ul>

<p><strong>3. PSYCHOSOZIALE FAKTOREN</strong></p>
<ul>
<li>Belastende Lebensereignisse</li>
<li>Aktuelle Belastungen</li>
<li>Soziale Unterstützung</li>
<li>Bewältigungsressourcen</li>
</ul>

<p><strong>4. FUNKTIONSBEEINTRÄCHTIGUNG</strong></p>
<ul>
<li>Berufliche Beeinträchtigung</li>
<li>Soziale Beeinträchtigung</li>
<li>Familiäre Beeinträchtigung</li>
<li>Grad der Beeinträchtigung</li>
</ul>

<p><strong>5. RISIKOFAKTOREN</strong></p>
<ul>
<li>Suizidalität</li>
<li>Selbstgefährdung</li>
<li>Fremdgefährdung</li>
<li>Suchtgefährdung</li>
</ul>

<p><strong>6. PROTECTIVE FAKTOREN</strong></p>
<ul>
<li>Soziale Unterstützung</li>
<li>Bewältigungsstrategien</li>
<li>Motivation zur Behandlung</li>
<li>Ressourcen</li>
</ul>

Die Diagnose sollte fundiert und für die Therapieplanung relevant sein.""",
    },
    "therapieplan": {
        "name": "Therapieplan",
        "prompt": """Erstelle einen strukturierten Therapieplan für eine psychotherapeutische Behandlung.

Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

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

<p><strong>1. DIAGNOSE UND INDIKATION</strong></p>
<ul>
<li>Hauptdiagnose</li>
<li>Indikation für Psychotherapie</li>
<li>Ausschlusskriterien</li>
<li>Kontraindikationen</li>
</ul>

<p><strong>2. THERAPIEZIELE</strong></p>
<ul>
<li>Primäre Ziele</li>
<li>Sekundäre Ziele</li>
<li>Kurzzeitziele</li>
<li>Langzeitziele</li>
<li>Erfolgskriterien</li>
</ul>

<p><strong>3. THERAPIEMETHODE</strong></p>
<ul>
<li>Gewählte Therapieform</li>
<li>Begründung der Wahl</li>
<li>Spezifische Techniken</li>
<li>Anpassungen an den Patienten</li>
</ul>

<p><strong>4. THERAPIEVERLAUF</strong></p>
<ul>
<li>Phase 1: Aufbau und Stabilisierung</li>
<li>Phase 2: Bearbeitung der Probleme</li>
<li>Phase 3: Konsolidierung und Abschluss</li>
<li>Übergänge zwischen Phasen</li>
</ul>

<p><strong>5. INTERVENTIONEN</strong></p>
<ul>
<li>Spezifische Interventionen</li>
<li>Hausaufgaben und Übungen</li>
<li>Kriseninterventionen</li>
<li>Rückfallprophylaxe</li>
</ul>

<p><strong>6. EVALUATION</strong></p>
<ul>
<li>Erfolgskontrolle</li>
<li>Messinstrumente</li>
<li>Zeitpunkte der Evaluation</li>
<li>Anpassung des Plans</li>
</ul>

<p><strong>7. ABSCHLUSSKRITERIEN</strong></p>
<ul>
<li>Kriterien für Therapieende</li>
<li>Nachsorgeplan</li>
<li>Rückfallprophylaxe</li>
<li>Wiedereinstiegskriterien</li>
</ul>

Der Therapieplan sollte strukturiert und für die Behandlung leitend sein.""",
    },
    "brief": {
        "name": "Brief",
        "prompt": """Erstelle einen professionellen Brief für einen Patienten oder andere Behandler.

Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

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

<p><strong>1. ANREDE UND EINLEITUNG</strong></p>
<ul>
<li>Professionelle Anrede</li>
<li>Bezug auf vorherige Kontakte</li>
<li>Anlass des Briefes</li>
</ul>

<p><strong>2. AKTUELLE SITUATION</strong></p>
<ul>
<li>Zusammenfassung der aktuellen Situation</li>
<li>Wichtige Entwicklungen</li>
<li>Aktuelle Beschwerden</li>
</ul>

<p><strong>3. THERAPIEVERLAUF</strong></p>
<ul>
<li>Wichtige Stationen der Behandlung</li>
<li>Erreichte Fortschritte</li>
<li>Verbleibende Herausforderungen</li>
</ul>

<p><strong>4. EMPFEHLUNGEN</strong></p>
<ul>
<li>Konkrete Empfehlungen</li>
<li>Weitere Schritte</li>
<li>Kooperation mit anderen Behandlern</li>
</ul>

<p><strong>5. ABSCHLUSS</strong></p>
<ul>
<li>Zusammenfassung</li>
<li>Dank und Wertschätzung</li>
<li>Professionelle Grußformel</li>
</ul>

Der Brief sollte professionell, respektvoll und für den Empfänger verständlich sein.""",
    },
    "other": {
        "name": "Sonstiges",
        "prompt": """Erstelle ein allgemeines Dokument für eine psychotherapeutische Behandlung.

Antworte in HTML-Format mit folgenden erlaubten Tags: <p>, <strong>, <ul>, <ol>, <li>

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

<p><strong>1. PATIENTENINFORMATIONEN</strong></p>
<ul>
<li>Relevante biografische Daten</li>
<li>Aktuelle Situation</li>
</ul>

<p><strong>2. THERAPIEINFORMATIONEN</strong></p>
<ul>
<li>Therapieverlauf</li>
<li>Wichtige Entwicklungen</li>
<li>Erreichte Fortschritte</li>
</ul>

<p><strong>3. FAZIT UND EMPFEHLUNGEN</strong></p>
<ul>
<li>Zusammenfassung</li>
<li>Empfehlungen für die Zukunft</li>
</ul>

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