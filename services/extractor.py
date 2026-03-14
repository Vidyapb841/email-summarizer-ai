# services/extractor.py
# Uses nltk + rules for extraction
# No API key needed — works offline forever

import re
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)

try:
    nltk.data.find('averaged_perceptron_tagger_eng')
except LookupError:
    nltk.download('averaged_perceptron_tagger_eng', quiet=True)


HIGH_KEYWORDS   = ["urgent", "critical", "asap", "immediately", "emergency",
                   "downtime", "alert", "deadline", "overdue", "blocked"]
MEDIUM_KEYWORDS = ["review", "update", "follow", "pending", "approval",
                   "meeting", "discuss", "proposal", "request", "schedule"]
ACTION_KEYWORDS = ["will", "prepare", "send", "review", "coordinate",
                   "submit", "complete", "finalize", "schedule", "please",
                   "must", "should", "needs to", "required", "action"]


def extract_details(summary: str, subject: str = "", participants: str = "") -> dict:
    text = (subject + " " + summary).lower()
    return {
        "key_topic":     _extract_topic(subject, summary),
        "action_items":  _extract_actions(summary),
        "owner":         _extract_owner(summary, participants),
        "followup_date": _extract_date(summary),
        "priority":      _detect_priority(text),
        "tags":          _extract_tags(text),
    }


def _extract_topic(subject: str, summary: str) -> str:
    if subject and subject.strip():
        return subject.strip()
    sentences = summary.split(".")
    return sentences[0].strip()[:80] if sentences else "General"


def _extract_actions(summary: str) -> str:
    sentences = re.split(r'[.!?]', summary)
    actions = []
    for s in sentences:
        if any(kw in s.lower() for kw in ACTION_KEYWORDS):
            s = s.strip()
            if len(s) > 10:
                actions.append(s)
    return "; ".join(actions[:3]) if actions else "None"


def _extract_owner(summary: str, participants: str) -> str:
    # Find Name + action word pattern
    match = re.search(r'\b([A-Z][a-z]+)\s+(will|to|should|must|needs)', summary)
    if match:
        return match.group(1)

    # Use nltk POS tagging to find proper nouns
    try:
        tokens = nltk.word_tokenize(summary)
        tags = nltk.pos_tag(tokens)
        for word, tag in tags:
            if tag == 'NNP' and len(word) > 2:
                return word
    except Exception:
        pass

    # Fallback to first participant
    if participants:
        first = participants.split("|")[0].strip()
        if "@" in first:
            return first.split("@")[0].replace(".", " ").title().split()[0]
        return first.split(",")[0].strip()

    return "Unassigned"


def _extract_date(summary: str) -> str:
    patterns = [
        r'\b(\d{4}-\d{2}-\d{2})\b',
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\b',
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
    ]
    for p in patterns:
        m = re.search(p, summary, re.IGNORECASE)
        if m:
            return m.group()
    return ""


def _detect_priority(text: str) -> str:
    if any(kw in text for kw in HIGH_KEYWORDS):
        return "High"
    if any(kw in text for kw in MEDIUM_KEYWORDS):
        return "Medium"
    return "Low"


def _extract_tags(text: str) -> str:
    tag_map = {
        "launch":     "Product Launch",
        "budget":     "Finance",
        "finance":    "Finance",
        "client":     "Client Relations",
        "meeting":    "Meeting",
        "server":     "IT Infrastructure",
        "downtime":   "IT Infrastructure",
        "policy":     "HR Policy",
        "sales":      "Sales",
        "feature":    "Product",
        "vendor":     "Procurement",
        "contract":   "Legal",
        "training":   "Training",
        "security":   "Security",
        "approval":   "Approval",
        "review":     "Review",
    }
    found = []
    for kw, tag in tag_map.items():
        if kw in text and tag not in found:
            found.append(tag)
        if len(found) >= 3:
            break
    return ", ".join(found) if found else "General"