import re

SYMPTOMS = {
    "fever": ["fever", "temperature", "high temperature", "feverish"],
    "cough": ["cough", "coughing"],
    "headache": ["headache", "head pain", "migraine"],
    "fatigue": ["fatigue", "tired", "tiredness", "weakness", "exhausted"],
    "sore_throat": ["sore throat", "throat pain"],
    "nausea": ["nausea", "nauseous", "feeling sick"],
    "vomiting": ["vomiting", "vomit", "threw up"],
    "diarrhea": ["diarrhea", "loose stools", "loose motion"],
    "rash": ["rash", "skin rash"],
    "joint_pain": ["joint pain", "joints hurt", "joint ache"],
    "chest_pain": ["chest pain", "pain in chest"],
    "breathlessness": ["shortness of breath", "breathless", "breathing difficulty"],
    "dizziness": ["dizzy", "dizziness", "lightheaded"]
}

def extract_symptoms(text: str):
    t = text.lower()
    found = []
    for key, phrases in SYMPTOMS.items():
        if any(re.search(r"\b"+re.escape(p)+r"\b", t) for p in phrases):
            found.append(key)
    days = None
    m = re.search(r"(\d+)\s*(day|days|week|weeks)", t)
    if m:
        n = int(m.group(1))
        days = n * (7 if "week" in m.group(2) else 1)
    return {"symptoms": found, "duration_days": days}
