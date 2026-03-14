# services/summarizer.py
# Uses sumy for AI-quality summarization
# No API key needed — works offline forever

import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# Download required nltk data silently
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)


def summarize_email(text: str, subject: str = "", participants: str = "") -> str:
    """Summarize email using sumy LSA algorithm."""
    try:
        full_text = f"{subject}. {text}"
        parser = PlaintextParser.from_string(full_text, Tokenizer("english"))
        summarizer = LsaSummarizer()
        sentences = summarizer(parser.document, 3)
        summary = " ".join(str(s) for s in sentences)
        if summary.strip():
            return summary.strip()
    except Exception:
        pass

    # Fallback
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
    return ". ".join(sentences[:2]) + "." if sentences else text[:200]