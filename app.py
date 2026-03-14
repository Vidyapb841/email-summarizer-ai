# app.py — Main Pipeline
# Run: python app.py

import os
import pandas as pd

from services.email_reader import read_emails
from services.summarizer   import summarize_email
from services.extractor    import extract_details
from utils.helper          import clean_text, remove_email_signature, remove_quoted_reply
from config.config         import EMAIL_SOURCE, CSV_OUTPUT_PATH


def run_pipeline():
    print("=" * 55)
    print("   📧 Group Email Summarizer — AI Pipeline")
    print("=" * 55)

    # Step 1: Read Emails
    print("\n🔄 Step 1: Loading emails from dataset...")
    emails = read_emails(source=EMAIL_SOURCE)

    if not emails:
        print("❌ No emails found. Check emails.csv in data/ folder.")
        return

    # Step 2: Process each thread
    print(f"\n🔄 Step 2: Processing {len(emails)} threads...")
    rows = []

    for i, email in enumerate(emails, 1):
        print(f"   [{i}/{len(emails)}] {email['thread'][:55]}...")

        body = clean_text(
            remove_quoted_reply(
                remove_email_signature(email["body"])
            )
        )

        summary = summarize_email(
            text=body,
            subject=email["thread"],
            participants=email["participants"],
        )

        details = extract_details(
            summary=summary,
            subject=email["thread"],
            participants=email["participants"],
        )

        rows.append({
            "Email Thread":    email["thread"],
            "Participants":    email["participants"],
            "Last Date":       email.get("date", ""),
            "No. of Messages": email.get("message_count", 1),
            "Summary":         summary,
            "Key Topic":       details.get("key_topic",     "—"),
            "Action Items":    details.get("action_items",  "None"),
            "Owner":           details.get("owner",         "Unassigned"),
            "Follow-up Date":  details.get("followup_date", "—"),
            "Priority":        details.get("priority",      "Medium"),
            "Tags":            details.get("tags",          ""),
        })

        print(f"      ✅ Topic: {rows[-1]['Key Topic']} | Owner: {rows[-1]['Owner']} | Priority: {rows[-1]['Priority']}")

    # Step 3: Save CSV
    print(f"\n🔄 Step 3: Saving to {CSV_OUTPUT_PATH}...")
    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(CSV_OUTPUT_PATH, index=False)
    print(f"✅ Saved {len(rows)} rows.")

    print("\n📋 Preview:")
    print(df[["Email Thread", "Key Topic", "Action Items", "Owner", "Priority"]].to_string(index=False))

    print("\n" + "=" * 55)
    print("✅ Pipeline complete! Now run:")
    print("   streamlit run dashboard/dashboard.py")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    run_pipeline()