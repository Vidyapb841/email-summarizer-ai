# prepare_data.py
# ─────────────────────────────────────────────
# Reads large Enron dataset and extracts
# 200 clean rows into a new small emails.csv
# Run: python prepare_data.py
# ─────────────────────────────────────────────

import pandas as pd
import re
import os

INPUT_FILE  = "data/emails.csv"       # large Enron dataset
OUTPUT_FILE = "data/emails_200.csv"   # clean 200 rows output
ROWS_NEEDED = 200


def clean_subject(subject: str) -> str:
    """Remove Re:, Fwd: prefixes."""
    subject = str(subject).strip()
    subject = re.sub(r'^(Re:|Fwd:|FW:|RE:|FWD:)\s*', '', subject, flags=re.IGNORECASE)
    return subject.strip()


def extract_body(raw: str) -> str:
    """Extract clean body from raw Enron email format."""
    raw = str(raw)
    # Enron emails have headers separated by blank line
    if "\n\n" in raw:
        parts = raw.split("\n\n", 1)
        body = parts[1] if len(parts) > 1 else raw
    else:
        body = raw

    # Remove forwarded/quoted lines
    lines = [l for l in body.split("\n")
             if not l.strip().startswith(">")
             and not l.strip().startswith("-----")
             and not l.strip().startswith("From:")
             and not l.strip().startswith("To:")
             and not l.strip().startswith("Subject:")
             and not l.strip().startswith("Date:")]

    body = " ".join(lines).strip()
    body = re.sub(r'\s+', ' ', body)
    return body[:500]   # cap at 500 chars


def extract_field(raw: str, field: str) -> str:
    """Extract a header field like From, To, Subject, Date."""
    match = re.search(rf'^{field}:\s*(.+)$', raw, re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def prepare_dataset():
    print("=" * 50)
    print("  📧 Enron Dataset Preparation")
    print("=" * 50)

    if not os.path.exists(INPUT_FILE):
        print(f"❌ File not found: {INPUT_FILE}")
        print("Place the Enron emails.csv inside the data/ folder.")
        return

    print(f"\n🔄 Reading large dataset: {INPUT_FILE}")
    print("   (This may take 30-60 seconds for large files...)")

    # Read in chunks to handle large file
    chunk_size = 5000
    collected  = []

    for chunk in pd.read_csv(INPUT_FILE, chunksize=chunk_size, on_bad_lines='skip'):
        for _, row in chunk.iterrows():
            raw = str(row.get("message", row.get("body", "")))

            subject = clean_subject(extract_field(raw, "Subject"))
            from_   = extract_field(raw, "From")
            to_     = extract_field(raw, "To")
            date_   = extract_field(raw, "Date")
            body    = extract_body(raw)

            # Skip empty or very short emails
            if len(body) < 30 or not subject:
                continue

            # Skip automated/system emails
            skip_words = ["unsubscribe", "auto-reply", "noreply",
                         "no-reply", "notification", "postmaster"]
            if any(w in from_.lower() for w in skip_words):
                continue

            collected.append({
                "message_id": len(collected) + 1,
                "subject":    subject if subject else "No Subject",
                "from":       from_,
                "to":         to_,
                "date":       date_,
                "body":       body,
            })

            if len(collected) >= ROWS_NEEDED:
                break

        if len(collected) >= ROWS_NEEDED:
            break

    if not collected:
        print("❌ No valid emails found. Check your CSV format.")
        return

    # Save output
    df = pd.DataFrame(collected[:ROWS_NEEDED])
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n✅ Done! Extracted {len(df)} clean emails.")
    print(f"✅ Saved to: {OUTPUT_FILE}")
    print(f"\n📋 Preview:")
    print(df[["subject", "from", "date"]].head(5).to_string(index=False))

    print(f"\n🔄 Now update config/config.py:")
    print(f'   EMAIL_CSV_PATH = "data/emails_200.csv"')
    print(f'   MAX_THREADS    = 200')
    print(f"\nThen run: python app.py")


if __name__ == "__main__":
    prepare_dataset()