"""Broad, educational health references for the CareBuddy prototype.

DDXPlus data is synthetic and limited to 49 pathologies. Its symptom overlap
matches are research-demo references, not calibrated probabilities or diagnoses.
"""
import html
import json
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

DDXPLUS_REVISION = "4a65d9b1de617ed3ec6f93172b5fa292553386bc"
DDXPLUS_BASE = (
    "https://huggingface.co/datasets/aai530-group6/ddxplus/raw/"
    + DDXPLUS_REVISION
    + "/"
)
DDXPLUS_FILES = {
    "conditions": DDXPLUS_BASE + "release_conditions.json",
    "evidences": DDXPLUS_BASE + "release_evidences.json",
}
MEDLINEPLUS_URL = "https://wsearch.nlm.nih.gov/ws/query"

SYMPTOM_ALIASES = {
    "fever": ("fever", "high temperature"),
    "cough": ("cough",),
    "chest_pain": ("chest pain", "pain in the chest"),
    "nausea": ("nausea", "feeling sick"),
    "headache": ("headache", "head pain"),
    "fatigue": ("fatigue", "tiredness", "feeling tired"),
    "stomach_pain": ("stomach pain", "abdominal pain", "belly pain"),
    "breathlessness": ("shortness of breath", "difficulty breathing", "breathlessness", "dyspnea"),
    "dizziness": ("dizziness", "dizzy", "vertigo"),
    "joint_pain": ("joint pain", "muscle pain", "myalgia", "arthralgia"),
    "sore_throat": ("sore throat", "throat pain"),
    "rash": ("rash", "skin lesion"),
}


def _get_json(url):
    request = Request(
        url,
        headers={"User-Agent": "CareBuddyHealthDemo/1.0 (educational health-topic references)"},
    )
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def load_ddxplus_metadata():
    """Fetch the small, pinned DDXPlus condition/evidence catalogs (not patient rows)."""
    return _get_json(DDXPLUS_FILES["conditions"]), _get_json(DDXPLUS_FILES["evidences"])


def related_condition_matches(symptoms, conditions, evidences, limit=8):
    """Rank benchmark conditions by exact symptom-tag overlap; never emit probabilities."""
    matched_evidence_ids = set()
    matched_questions = {}
    for symptom in set(symptoms or []):
        aliases = SYMPTOM_ALIASES.get(symptom, ())
        if not aliases:
            continue
        for evidence_id, evidence in evidences.items():
            if evidence.get("is_antecedent"):
                continue
            question = str(evidence.get("question_en", "")).lower()
            if any(alias in question for alias in aliases):
                matched_evidence_ids.add(evidence_id)
                matched_questions[evidence_id] = str(
                    evidence.get("question_en", symptom.replace("_", " "))
                )

    if not matched_evidence_ids:
        return []

    results = []
    for condition in conditions.values():
        condition_evidence = set((condition.get("symptoms") or {}).keys())
        overlap = sorted(matched_evidence_ids & condition_evidence)
        if overlap:
            name = str(condition.get("condition_name", "")).strip()
            if name:
                results.append({
                    "condition": name,
                    "match_count": len(overlap),
                    "matched_symptoms": [matched_questions[item] for item in overlap],
                })
    results.sort(key=lambda item: (-item["match_count"], item["condition"].casefold()))
    return results[:limit]


def _plain_text(value):
    value = re.sub(r"<[^>]+>", " ", value or "")
    return html.unescape(re.sub(r"\s+", " ", value)).strip()


def search_medlineplus_topics(condition_name, limit=3):
    """Search NLM MedlinePlus by condition title, returning attributed topic summaries."""
    params = urlencode({
        "db": "healthTopics",
        "term": "title:" + condition_name,
        "retmax": str(limit),
        "rettype": "brief",
        "tool": "carebuddyhealthdemo",
    })
    request = Request(
        MEDLINEPLUS_URL + "?" + params,
        headers={"User-Agent": "CareBuddyHealthDemo/1.0 (educational health-topic references)"},
    )
    with urlopen(request, timeout=12) as response:
        root = ET.fromstring(response.read())

    results = []
    for document in root.findall(".//document"):
        item = {"url": document.attrib.get("url", "")}
        for element in document.findall("content"):
            name = str(element.attrib.get("name", "")).lower()
            if name in ("title", "fullsummary", "snippet"):
                item[name] = _plain_text("".join(element.itertext()))
        if item.get("url", "").startswith("https://medlineplus.gov/") and item.get("title"):
            results.append(item)
    return results
