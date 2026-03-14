# services/email_reader.py
# ─────────────────────────────────────────────
# Reads email threads from local CSV dataset
# ─────────────────────────────────────────────

import pandas as pd
from config.config import MAX_THREADS, EMAIL_CSV_PATH


def read_emails(source: str = None) -> list:
    """Load emails from local CSV. Returns list of thread dicts."""
    print(f"📥 Loading emails from: {EMAIL_CSV_PATH}")

    try:
        df = pd.read_csv(EMAIL_CSV_PATH)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Dataset not found at {EMAIL_CSV_PATH}\n"
            "Place your emails.csv inside the data/ folder."
        )

    df = df.head(MAX_THREADS)

    emails = []
    for _, row in df.iterrows():
        emails.append({
            "thread":        str(row.get("subject", "No Subject")),
            "from":          str(row.get("from", "")),
            "to":            str(row.get("to", "")),
            "date":          str(row.get("date", "")),
            "participants":  _get_participants(row),
            "message_count": 1,
            "body":          str(row.get("body", ""))[:3000],
        })

    print(f"✅ Loaded {len(emails)} email threads.")
    return emails


def _get_participants(row) -> str:
    parts = []
    for field in ("from", "to"):
        val = str(row.get(field, "")).strip()
        if val and val != "nan":
            parts.append(val)
    return " | ".join(parts)