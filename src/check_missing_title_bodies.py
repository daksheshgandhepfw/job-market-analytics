import csv
import re

INPUT_FILE = "data/processed/enriched_job_emails_with_titles.csv"
OUTPUT_FILE = "data/processed/missing_title_body_audit.txt"

BODY_PREVIEW_LENGTH = 1800


def clean_body(body):
    if not body:
        return ""

    # Normalize whitespace while preserving readable lines.
    body = body.replace("\r\n", "\n").replace("\r", "\n")

    # Remove excessive blank lines.
    body = re.sub(r"\n{3,}", "\n\n", body)

    # Remove excessive spaces/tabs.
    body = re.sub(r"[ \t]+", " ", body)

    return body.strip()


with open(INPUT_FILE, "r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    records = list(reader)


missing_records = [
    record
    for record in records
    if record.get("job_title_source", "").strip() == "MISSING"
]


with open(OUTPUT_FILE, "w", encoding="utf-8") as output:

    output.write(f"Total records: {len(records)}\n")
    output.write(f"Missing-title records: {len(missing_records)}\n\n")

    output.write("=== MISSING TITLE BODY AUDIT ===\n\n")

    for record in missing_records:

        body = clean_body(record.get("email_body", ""))

        preview = body[:BODY_PREVIEW_LENGTH]

        output.write("-" * 80 + "\n")
        output.write(
            f"Email ID: {record.get('email_id', '')}\n"
        )
        output.write(
            f"Company: {record.get('company_name', '')}\n"
        )
        output.write(
            f"Raw Title: {record.get('raw_job_title', '')}\n"
        )
        output.write(
            f"Subject: {record.get('subject', '')}\n"
        )
        output.write(
            f"Sender: {record.get('sender', '')}\n"
        )
        output.write(
            f"Body Length: {len(body)}\n"
        )

        output.write("\nBODY PREVIEW:\n")

        if preview:
            output.write(preview)
        else:
            output.write("[NO BODY AVAILABLE]")

        if len(body) > BODY_PREVIEW_LENGTH:
            output.write("\n...[TRUNCATED]")

        output.write("\n\n")