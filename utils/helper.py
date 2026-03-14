# utils/helper.py
# ─────────────────────────────────────────────
# Text cleaning and formatting utilities
# ─────────────────────────────────────────────

import re


def clean_text(text: str) -> str:
    """Remove extra whitespace and non-ASCII characters."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    return text.strip()


def remove_email_signature(text: str) -> str:
    """Strip common email signature patterns."""
    patterns = [
        r"--\s*\n.*",
        r"Best regards.*",
        r"Thanks and regards.*",
        r"Regards,.*",
        r"Thanks,.*",
        r"Sent from my.*",
    ]
    for p in patterns:
        text = re.sub(p, "", text, flags=re.IGNORECASE | re.DOTALL)
    return text.strip()


def remove_quoted_reply(text: str) -> str:
    """Remove quoted reply lines starting with >."""
    lines = [l for l in text.split("\n") if not l.strip().startswith(">")]
    return "\n".join(lines).strip()


def format_action_items(raw: str) -> list:
    """Convert semicolon-separated string to a Python list."""
    if not raw or raw.lower() == "none":
        return []
    return [item.strip() for item in raw.split(";") if item.strip()]


def truncate(text: str, max_len: int = 80) -> str:
    """Truncate text for display."""
    return text if len(text) <= max_len else text[:max_len] + "…"