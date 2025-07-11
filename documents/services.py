from typing import Dict, Any
from core.connector import get_llm_connector
from .prompts import get_document_prompt, DOCUMENT_SYSTEM_PROMPT
from patients.models import Patient
from therapy.models import Therapy


class DocumentService:
    """Service for generating therapy documents using AI"""
    
    def __init__(self):
        self.connector = get_llm_connector()
    
    def is_available(self) -> bool:
        """Check if the document service is available"""
        return self.connector.is_available()
    
    def generate(self, patient: Patient, therapy: Therapy, document_type: str) -> str:
        """
        Generate a document of the specified type for a patient and therapy
        
        Args:
            patient: The patient for whom to generate the document
            therapy: The therapy context
            document_type: Type of document to generate (e.g., 'abschlussbericht')
            
        Returns:
            Generated document content
        """
        if not self.is_available():
            raise ValueError("OpenAI API key ist nicht konfiguriert")
        
        try:
            # Get the appropriate prompt template
            prompt = get_document_prompt(document_type)
            
            # Prepare context data
            context_data = self._prepare_context_data(patient, therapy)
            
            # Format the prompt with context data
            formatted_prompt = prompt.format(**context_data)
            
            # Generate the document using the document-specific system prompt
            return self.connector.generate_text(
                system_prompt=DOCUMENT_SYSTEM_PROMPT,
                user_prompt=formatted_prompt,
                max_tokens=2000,
                temperature=0.3
            )
            
        except Exception as e:
            raise Exception(f"Fehler bei der Dokumentgenerierung: {str(e)}")
    
    def _prepare_context_data(self, patient: Patient, therapy: Therapy) -> Dict[str, Any]:
        """
        Prepare context data for document generation
        
        Args:
            patient: The patient
            therapy: The therapy
            
        Returns:
            Dictionary with context data
        """
        # Get all sessions for this therapy
        sessions = therapy.session_set.order_by('date')
        
        # Get all transcriptions for this therapy
        transcriptions = []
        for session in sessions:
            for recording in session.audiorecording_set.all():
                if hasattr(recording, 'transcription') and recording.transcription:
                    transcriptions.append({
                        'session_date': session.date.strftime('%d.%m.%Y'),
                        'session_title': session.title or f"Sitzung vom {session.date.strftime('%d.%m.%Y')}",
                        'text': recording.transcription.text,
                        'summary': session.summary or "Keine Zusammenfassung verfügbar"
                    })
        
        # Prepare patient information (anonymized)
        patient_info = {
            'age': patient.age if hasattr(patient, 'age') else "Nicht angegeben",
            'gender': patient.gender if hasattr(patient, 'gender') else "Nicht angegeben",
            'occupation': getattr(patient, 'occupation', 'Nicht angegeben'),
            'marital_status': getattr(patient, 'marital_status', 'Nicht angegeben'),
        }
        
        # Prepare therapy information
        therapy_info = {
            'start_date': therapy.start_date.strftime('%d.%m.%Y'),
            'end_date': therapy.end_date.strftime('%d.%m.%Y') if therapy.end_date else "Laufend",
            'status': therapy.get_status_display(),
            'goals': therapy.goals or "Keine Ziele definiert",
            'notes': therapy.notes or "Keine Notizen verfügbar",
            'session_count': sessions.count(),
        }
        
        return {
            'patient_info': patient_info,
            'therapy_info': therapy_info,
            'sessions': sessions,
            'transcriptions': transcriptions,
            'patient': patient,
            'therapy': therapy,
        } 