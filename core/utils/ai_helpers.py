"""AI-related helper functions shared across services"""


def build_gender_context(patient_gender: str = None) -> str:
    """
    Build gender context for AI prompts
    
    Args:
        patient_gender: The patient's gender ('male', 'female', 'diverse', 'not_specified')
        
    Returns:
        Formatted gender context string for AI prompts
    """
    if not patient_gender or patient_gender == "not_specified":
        return ""

    gender_mapping = {"male": "männlich", "female": "weiblich", "diverse": "divers"}
    gender_display = gender_mapping.get(patient_gender, "nicht angegeben")

    pronouns_mapping = {
        "male": "er/ihm/sein",
        "female": "sie/ihr/ihre",
        "diverse": "sie/dey/deren (verwende geschlechtsneutrale Sprache)",
    }
    pronouns = pronouns_mapping.get(patient_gender, "")

    return f"""**PATIENT*INNEN-INFORMATIONEN**
Das Geschlecht des Patienten ist {gender_display}. Verwende entsprechende Pronomen ({pronouns}) und
geschlechtsangemessene Sprache. Achte auf eine respektvolle und professionelle Darstellung.

""" 