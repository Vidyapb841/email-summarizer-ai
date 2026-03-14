# services/extractor.py
# Key Topic extracted from EMAIL CONTENT not just subject

import re
import nltk

for resource in ['punkt', 'punkt_tab', 'averaged_perceptron_tagger',
                 'averaged_perceptron_tagger_eng']:
    try:
        nltk.data.find(f'tokenizers/{resource}')
    except LookupError:
        try:
            nltk.data.find(f'taggers/{resource}')
        except LookupError:
            nltk.download(resource, quiet=True)

HIGH_KEYWORDS   = ["urgent","critical","asap","immediately","emergency",
                   "downtime","alert","deadline","overdue","blocked",
                   "important","priority","escalate","risk","issue","error"]
MEDIUM_KEYWORDS = ["review","update","follow","pending","approval","meeting",
                   "discuss","proposal","request","schedule","reminder",
                   "confirm","response","required","needed","attached","fyi"]
ACTION_PATTERNS = [
    r'\b([A-Z][a-z]+ will [\w\s]{3,40})',
    r'\b(please [\w\s]{3,50})',
    r'\b(can you [\w\s]{3,40})',
    r'\b(could you [\w\s]{3,40})',
    r'\b(needs? to [\w\s]{3,40})',
    r'\b(must [\w\s]{3,30})',
    r'\b(should [\w\s]{3,30})',
    r'\b(let me know[\w\s]{0,40})',
    r'\b(follow.?up[\w\s]{0,30})',
    r'\b(send [\w\s]{3,40})',
    r'\b(schedule [\w\s]{3,30})',
    r'\b(deadline[\w\s]{0,30})',
    r'\b(due [\w\s]{3,25})',
    r'\b(action [\w\s]{3,30})',
    r'\b(call [\w\s]{3,30})',
    r'\b(check [\w\s]{3,30})',
    r'\b(review [\w\s]{3,30})',
    r'\b(confirm [\w\s]{3,30})',
    r'\b(attached [\w\s]{3,40})',
    r'\b(see (?:attached|below|above)[\w\s]{0,30})',
    r'\b(we need [\w\s]{3,40})',
    r'\b(I need [\w\s]{3,40})',
    r'\b(need (?:to|your) [\w\s]{3,40})',
    r'\b(make sure [\w\s]{3,40})',
    r'\b(respond [\w\s]{0,30})',
    r'\b(reply [\w\s]{0,30})',
    r'\b(get back [\w\s]{0,30})',
]
DATE_PATTERNS = [
    r'\b(\d{4}-\d{2}-\d{2})\b',
    r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\.?\s+\d{1,2}\w*,?\s*\d{0,4}\b',
    r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
    r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
    r'\b(tomorrow|next week|next month|end of week|eod|eow|tonight)\b',
    r'\bby (?:the end|close|noon|morning|afternoon|evening|Friday|Monday)\b',
    r'\bthis (?:week|month|Friday|Monday|Tuesday|Wednesday|Thursday)\b',
    r'\b(today|tonight)\b',
    r'\b\d{1,2}\s+(?:days?|weeks?|months?)\b',
]
TAG_MAP = {
    "launch":"Product Launch","release":"Product Launch",
    "budget":"Finance","finance":"Finance","payment":"Finance","invoice":"Finance",
    "client":"Client Relations","customer":"Client Relations",
    "meeting":"Meeting","call":"Meeting","conference":"Meeting",
    "server":"IT","system":"IT","network":"IT","downtime":"IT",
    "policy":"HR","hr":"HR","employee":"HR",
    "sales":"Sales","revenue":"Sales","deal":"Sales",
    "contract":"Legal","legal":"Legal","agreement":"Legal",
    "training":"Training","security":"Security",
    "report":"Reporting","data":"Reporting",
    "energy":"Energy","gas":"Energy","power":"Energy",
    "trade":"Trading","market":"Market","price":"Pricing",
    "attached":"Document","attachment":"Document",
    "update":"Update","fyi":"FYI",
}
SKIP_NAMES = {
    "The","This","That","Please","We","Our","Your","Any","All","For",
    "If","In","On","At","By","To","From","Hi","Hello","Dear","Thanks",
    "Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday",
    "January","February","March","April","May","June","July","August",
    "September","October","November","December","Today","Tomorrow",
    "Just","Also","Here","There","When","What","How","Why","Who",
}

# ── Content-based topic mappings ──────────────────────────────────────────────
TOPIC_MAPPINGS = [
    # Finance
    (r"budget|cost|expense|invoice|payment|spend|financial|fund|reimburse",
     "Budget & Finance Discussion"),
    (r"revenue|profit|loss|quarterly|q1|q2|q3|q4|earnings|forecast",
     "Financial Performance Review"),
    # IT & Systems
    (r"server|system|network|downtime|outage|crash|incident|production issue",
     "Production System Issue"),
    (r"deploy|deployment|release|launch|go.live|rollout",
     "Product Release Planning"),
    # HR
    (r"employee|staff|hire|resign|leave|vacation|policy|hr|payroll|benefit",
     "HR & People Management"),
    (r"training|workshop|course|learn|certification|skill",
     "Training & Development"),
    # Business
    (r"client|customer|account|contract|deal|proposal|negotiat",
     "Client Relationship Management"),
    (r"sales|target|quota|pipeline|lead|prospect|conversion",
     "Sales Performance"),
    (r"legal|compliance|regulation|audit|risk|liability",
     "Legal & Compliance"),
    (r"project|milestone|deliverable|timeline|roadmap|sprint",
     "Project Management"),
    (r"meeting|agenda|minutes|conference|standup",
     "Team Meeting"),
    (r"report|analysis|data|metrics|kpi|dashboard|insight",
     "Data & Reporting"),
    # Energy (Enron specific)
    (r"energy|gas|power|electricity|transmission|pipeline",
     "Energy Operations"),
    (r"trade|trading|commodity|futures|market|price|bid|offer",
     "Energy Trading"),
    (r"california|texas|northwest|southwest|capacity|load",
     "Power Market Operations"),
    # Communication
    (r"attach|document|file|spreadsheet|presentation",
     "Document Sharing"),
    (r"approval|approve|sign.?off|authorize|permission",
     "Approval Request"),
    (r"confirm|confirmation|acknowledge|receipt",
     "Confirmation Required"),
    (r"issue|problem|bug|fix|resolve|solution|troubleshoot",
     "Issue Resolution"),
    (r"urgent|critical|asap|immediately|emergency",
     "Urgent Action Required"),
    (r"update|status|progress|follow.?up|reminder",
     "Progress Update"),
    (r"question|query|clarif|help|assist|support",
     "Query & Support"),
    (r"offer|opportunity|partnership|collaborat",
     "Business Opportunity"),
]


def extract_details(summary: str, subject: str = "", participants: str = "",
                    body: str = "") -> dict:
    text = (subject + " " + summary + " " + body).lower()
    return {
        "key_topic":     _extract_topic(subject, summary, body),
        "action_items":  _extract_actions(summary),
        "owner":         _extract_owner(summary, participants),
        "followup_date": _extract_date(summary),
        "priority":      _detect_priority(text),
        "tags":          _extract_tags(text),
    }


def _extract_topic(subject: str, summary: str = "", body: str = "") -> str:
    """
    KEY TOPIC = what the conversation is ABOUT (from content).
    EMAIL THREAD = conversation name (subject line).
    These must be DIFFERENT.
    """
    combined = (summary + " " + body + " " + subject).lower()

    for pattern, topic in TOPIC_MAPPINGS:
        if re.search(pattern, combined):
            return topic

    # Fallback: rephrase subject as topic
    if subject and subject.strip() not in ("", "No Subject"):
        clean = re.sub(r'^(Re:|Fwd:|FW:|RE:|FWD:)\s*', '', subject,
                       flags=re.IGNORECASE)
        clean = re.sub(r'\s+', ' ', clean).strip()
        words = [w for w in clean.split() if len(w) > 2]
        if words:
            return " ".join(words[:4]) + " Discussion"

    return "General Business Discussion"


def _extract_actions(summary: str) -> str:
    clean = re.sub(r'\b[A-Z]+/[A-Z]+/[A-Z]+@[A-Z]+\b', '', summary)
    clean = re.sub(r'\d{2}/\d{2}/\d{4}\s*\d{0,2}:?\d{0,2}\s*(?:AM|PM)?', '', clean)
    clean = re.sub(r'\b[A-Z]{4,}\b', '', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()

    found = []
    for pattern in ACTION_PATTERNS:
        for match in re.finditer(pattern, clean, re.IGNORECASE):
            action = match.group(1).strip() if match.lastindex else match.group().strip()
            action = re.sub(r'\s+', ' ', action).strip()
            if 8 <= len(action) <= 120 and re.search(r'[a-zA-Z]{3,}', action):
                if action not in found:
                    found.append(action)
        if len(found) >= 3:
            break

    if found:
        return "; ".join(found[:3])

    sentences = [s.strip() for s in re.split(r'[.!?\n]', clean) if len(s.strip()) > 15]
    for s in sentences:
        try:
            tokens = nltk.word_tokenize(s)
            tags   = nltk.pos_tag(tokens)
            if any(t in ('VB','VBD','VBG','VBN','VBP','VBZ') for _, t in tags):
                if s not in found:
                    found.append(s[:120])
                if len(found) >= 2:
                    break
        except Exception:
            pass

    if found:
        return "; ".join(found[:2])

    if sentences:
        return sentences[0][:120]

    return "Review email for details"


def _extract_owner(summary: str, participants: str) -> str:
    clean = re.sub(r'\b[A-Z]+/[A-Z]+@[A-Z]+\b', '', summary)

    patterns = [
        r'\b([A-Z][a-z]{2,15})\s+will\b',
        r'\b([A-Z][a-z]{2,15})\s+should\b',
        r'\b([A-Z][a-z]{2,15})\s+needs?\s+to\b',
        r'\bcontact\s+([A-Z][a-z]{2,15})\b',
        r'\b([A-Z][a-z]{2,15})\s+is\s+responsible\b',
        r'\b([A-Z][a-z]{2,15})\s+has\s+(?:agreed|confirmed)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, clean)
        if match:
            name = match.group(1)
            if name not in SKIP_NAMES:
                return name

    try:
        tokens = nltk.word_tokenize(clean[:500])
        tags   = nltk.pos_tag(tokens)
        for word, tag in tags:
            if tag == 'NNP' and len(word) > 2 and word not in SKIP_NAMES:
                return word
    except Exception:
        pass

    if participants:
        first = participants.split("|")[0].strip()
        if "@" in first:
            name = first.split("@")[0].replace(".", " ").replace("_", " ").title()
            return name.split()[0] if name else "Unassigned"
        return first.split(",")[0].strip()[:20]

    return "Unassigned"


def _extract_date(summary: str) -> str:
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, summary, re.IGNORECASE)
        if match:
            return match.group().strip()
    year_match = re.search(r'\b(200[0-9]|201[0-9]|202[0-9])\b', summary)
    if year_match:
        return year_match.group()
    return "Not specified"


def _detect_priority(text: str) -> str:
    if any(kw in text for kw in HIGH_KEYWORDS):
        return "High"
    if any(kw in text for kw in MEDIUM_KEYWORDS):
        return "Medium"
    return "Low"


def _extract_tags(text: str) -> str:
    found = []
    for kw, tag in TAG_MAP.items():
        if kw in text and tag not in found:
            found.append(tag)
        if len(found) >= 3:
            break
    return ", ".join(found) if found else "General"