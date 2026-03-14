# services/summarizer.py
# Enhanced sumy summarizer with better cleaning

import re
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

for resource in ['punkt', 'punkt_tab']:
    try:
        nltk.data.find(f'tokenizers/{resource}')
    except LookupError:
        nltk.download(resource, quiet=True)


def summarize_email(text: str, subject: str = "", participants: str = "") -> str:
    """Summarize using sumy LSA with better preprocessing."""

    # Pre-clean for summarizer
    text = _preprocess(text)

    if len(text) < 30:
        return f"Email about {subject}." if subject else "No content available."

    try:
        full_text = text
        parser    = PlaintextParser.from_string(full_text, Tokenizer("english"))
        summarizer = LsaSummarizer()
        sentences  = summarizer(parser.document, 2)   # 2 sentences only
        summary    = " ".join(str(s) for s in sentences).strip()

        if summary and len(summary) > 20:
            return summary

    except Exception:
        pass

    # Fallback: first 2 clean sentences
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if len(s.strip()) > 20]
    if sentences:
        return ". ".join(sentences[:2]) + "."

    return f"Discussion about {subject}." if subject else text[:200]


def _preprocess(text: str) -> str:
    """Clean text specifically for summarization."""
    # Remove email-style headers inside body
    text = re.sub(r'\b[A-Z]{2,}\b[\s/]+[A-Z]{2,}\b', '', text)   # TIM/HOU/ECT
    text = re.sub(r'\b\w+@\w+\b', '', text)                        # emails
    text = re.sub(r'\d{2}/\d{2}/\d{4}', '', text)                  # dates
    text = re.sub(r'\d{1,2}:\d{2}\s*(AM|PM)', '', text)            # times
    text = re.sub(r'[A-Z]{5,}', '', text)                           # ALL CAPS words
    text = re.sub(r'\s+', ' ', text)                                # whitespace
    return text.strip()