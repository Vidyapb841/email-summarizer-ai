# utils/helper.py
# Enhanced text cleaning for Enron email format

import re


def clean_text(text: str) -> str:
    """Full clean pipeline for Enron emails."""
    text = remove_email_headers(text)
    text = remove_quoted_reply(text)
    text = remove_email_signature(text)
    text = remove_timestamps(text)
    text = remove_special_chars(text)
    return text.strip()


def remove_email_headers(text: str) -> str:
    """Remove email header lines like From/To/Date/Subject/cc."""
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        l = line.strip()
        # Skip header-style lines
        if re.match(r'^(From|To|Subject|Date|Cc|Bcc|Sent|Message-ID|X-|Content)[\s:]+', l, re.IGNORECASE):
            continue
        # Skip lines that look like "NAME DATE TIME" headers
        if re.match(r'^[A-Z\s]+\d{2}/\d{2}/\d{4}', l):
            continue
        # Skip lines with just email addresses
        if re.match(r'^[\w\.\-]+@[\w\.\-]+$', l):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def remove_timestamps(text: str) -> str:
    """Remove timestamp patterns like 04/25/2000 11:43 AM."""
    text = re.sub(r'\d{2}/\d{2}/\d{4}\s+\d{1,2}:\d{2}\s*(AM|PM)', '', text)
    text = re.sub(r'\d{1,2}:\d{2}\s*(AM|PM)', '', text)
    return text


def remove_quoted_reply(text: str) -> str:
    """Remove quoted reply lines."""
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        l = line.strip()
        if l.startswith(">"):
            continue
        if re.match(r'^-{3,}', l):
            break   # stop at forwarded message separator
        if re.match(r'^\*{3,}', l):
            break
        cleaned.append(line)
    return "\n".join(cleaned)


def remove_email_signature(text: str) -> str:
    """Remove common signature patterns."""
    patterns = [
        r'(Best regards?|Regards?|Thanks?|Sincerely|Cheers)[,\s].*',
        r'Sent from my.*',
        r'_{3,}.*',
    ]
    for p in patterns:
        text = re.sub(p, '', text, flags=re.IGNORECASE | re.DOTALL)
    return text


def remove_special_chars(text: str) -> str:
    """Clean up whitespace and non-printable chars."""
    text = re.sub(r'[^\x20-\x7E\n]', ' ', text)   # keep only printable ASCII
    text = re.sub(r'\n{3,}', '\n\n', text)          # max 2 newlines
    text = re.sub(r' {2,}', ' ', text)              # collapse spaces
    return text.strip()


def remove_forwarded_block(text: str) -> str:
    """Remove forwarded email blocks."""
    # Remove everything after forwarded message markers
    markers = [
        r'-----\s*Original Message\s*-----',
        r'-----\s*Forwarded.*?-----',
        r'_{5,}',
    ]
    for marker in markers:
        text = re.split(marker, text, flags=re.IGNORECASE)[0]
    return text.strip()


def truncate(text: str, max_len: int = 80) -> str:
    return text if len(text) <= max_len else text[:max_len] + "…"