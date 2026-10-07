import csv
from collections import Counter


INPUT_FILE = "data/processed/enriched_job_emails_with_titles.csv"
OUTPUT_FILE = "data/processed/enriched_job_title_audit.txt"


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    records = list(reader)


existing = [
    r for r in records
    if r["job_title_source"] == "EXISTING"
]

subject = [
    r for r in records
    if r["job_title_source"] == "SUBJECT"
]

missing = [
    r for r in records
    if r["job_title_source"] == "MISSING"
]


subject_titles = Counter(
    r["job_title"].strip()
    for r in subject
    if r["job_title"].strip()
)


with open(OUTPUT_FILE, "w", encoding="utf-8") as out:

    out.write(f"Total records: {len(records)}\n")
    out.write(f"EXISTING: {len(existing)}\n")
    out.write(f"SUBJECT: {len(subject)}\n")
    out.write(f"MISSING: {len(missing)}\n")


    # ------------------------------------------
    # ALL SUBJECT-DERIVED TITLES
    # ------------------------------------------

    out.write(
        "\n=== SUBJECT-DERIVED TITLES ===\n"
    )

    for r in subject:

        out.write(
            "\n----------------------------------------\n"
        )

        out.write(
            f"Email ID: {r['email_id']}\n"
        )

        out.write(
            f"Company: {r['company_name']}\n"
        )

        out.write(
            f"Raw Title: {r['raw_job_title']}\n"
        )

        out.write(
            f"Enriched Title: {r['job_title']}\n"
        )

        out.write(
            f"Subject: {r['subject']}\n"
        )

        out.write(
            f"Sender: {r['sender']}\n"
        )


    # ------------------------------------------
    # UNRESOLVED TITLES
    # ------------------------------------------

    out.write(
        "\n\n=== MISSING TITLES ===\n"
    )

    for r in missing:

        out.write(
            "\n----------------------------------------\n"
        )

        out.write(
            f"Email ID: {r['email_id']}\n"
        )

        out.write(
            f"Company: {r['company_name']}\n"
        )

        out.write(
            f"Raw Title: {r['raw_job_title']}\n"
        )

        out.write(
            f"Subject: {r['subject']}\n"
        )

        out.write(
            f"Sender: {r['sender']}\n"
        )


print(f"Subject-derived titles: {len(subject)}")
print(f"Missing titles: {len(missing)}")
print(f"Created: {OUTPUT_FILE}")