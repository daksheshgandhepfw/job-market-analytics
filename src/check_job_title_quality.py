import csv
from collections import Counter


INPUT_FILE = "data/processed/enriched_job_emails.csv"
OUTPUT_FILE = "data/processed/job_title_quality_audit.txt"


records = []

with open(INPUT_FILE, "r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    records = list(reader)


# --------------------------------------------------
# BASIC QUALITY COUNTS
# --------------------------------------------------

missing_titles = [
    record
    for record in records
    if not record["job_title"].strip()
]

present_titles = [
    record
    for record in records
    if record["job_title"].strip()
]


# --------------------------------------------------
# SUSPICIOUS TITLE DETECTION
# --------------------------------------------------

suspicious_exact = {
    "a",
    "an",
    "the",
    "following",
    "position",
    "role",
    "job",
    "opportunity",
    "career opportunities",
    "application",
    "your application",
    "this position",
    "this role",
}


suspicious_fragments = [
    "thank you for",
    "thanks for",
    "your interest",
    "our interest",
    "your application",
    "application has",
    "application was",
    "application received",
    "career opportunities",
    "click here",
    "http://",
    "https://",
]


suspicious_titles = []

for record in present_titles:
    title = record["job_title"].strip()
    title_lower = title.lower()

    reasons = []

    if title_lower in suspicious_exact:
        reasons.append("SUSPICIOUS_EXACT")

    if any(
        fragment in title_lower
        for fragment in suspicious_fragments
    ):
        reasons.append("SUSPICIOUS_FRAGMENT")

    # Extremely short titles are often extraction errors.
    if len(title) <= 2:
        reasons.append("VERY_SHORT")

    # Very long extracted text is often prose rather than a title.
    if len(title.split()) > 15:
        reasons.append("VERY_LONG")

    if reasons:
        suspicious_titles.append({
            **record,
            "suspicion_reason": "|".join(reasons)
        })


# --------------------------------------------------
# TITLE FREQUENCIES
# --------------------------------------------------

title_counts = Counter(
    record["job_title"].strip()
    for record in present_titles
)


# --------------------------------------------------
# WRITE AUDIT
# --------------------------------------------------

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as output:

    output.write(
        f"Total job-related emails: {len(records)}\n"
    )

    output.write(
        f"Titles present: {len(present_titles)}\n"
    )

    output.write(
        f"Missing job titles: {len(missing_titles)}\n"
    )

    completeness = (
        len(present_titles) / len(records) * 100
        if records else 0
    )

    output.write(
        f"Job title completeness: {completeness:.1f}%\n"
    )

    output.write(
        f"Suspicious existing titles: "
        f"{len(suspicious_titles)}\n"
    )


    # --------------------------------------------------
    # COMMON TITLES
    # --------------------------------------------------

    output.write(
        "\n=== MOST COMMON EXISTING JOB TITLES ===\n"
    )

    for title, count in title_counts.most_common(40):
        output.write(
            f"{count:>3} | {title}\n"
        )


    # --------------------------------------------------
    # SUSPICIOUS TITLES
    # --------------------------------------------------

    output.write(
        "\n=== SUSPICIOUS EXISTING JOB TITLES ===\n"
    )

    for record in suspicious_titles:

        output.write(
            "\n----------------------------------------\n"
        )

        output.write(
            f"Email ID: {record['email_id']}\n"
        )

        output.write(
            f"Company: {record['company_name']}\n"
        )

        output.write(
            f"Extracted Title: {record['job_title']}\n"
        )

        output.write(
            f"Reason: {record['suspicion_reason']}\n"
        )

        output.write(
            f"Subject: {record['subject']}\n"
        )

        output.write(
            f"Sender: {record['sender']}\n"
        )


    # --------------------------------------------------
    # MISSING TITLES
    # --------------------------------------------------

    output.write(
        "\n=== MISSING JOB TITLES ===\n"
    )

    for record in missing_titles:

        output.write(
            "\n----------------------------------------\n"
        )

        output.write(
            f"Email ID: {record['email_id']}\n"
        )

        output.write(
            f"Company: {record['company_name']}\n"
        )

        output.write(
            f"Subject: {record['subject']}\n"
        )

        output.write(
            f"Sender: {record['sender']}\n"
        )


print(f"Total job-related emails: {len(records)}")
print(f"Titles present: {len(present_titles)}")
print(f"Missing job titles: {len(missing_titles)}")
print(
    f"Job title completeness: "
    f"{completeness:.1f}%"
)
print(
    f"Suspicious existing titles: "
    f"{len(suspicious_titles)}"
)

print(f"\nCreated: {OUTPUT_FILE}")