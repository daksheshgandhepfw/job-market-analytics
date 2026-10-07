import csv
import re
from collections import Counter


INPUT_FILE = "data/processed/enriched_job_emails.csv"
OUTPUT_FILE = "data/processed/company_value_quality_audit.txt"


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    records = list(reader)


# --------------------------------------------------
# SUSPICIOUS COMPANY RULES
# --------------------------------------------------

suspicious_exact = {
    "application received",
    "confirmation",
    "joining our team",
    "our team",
    "the position",
    "this position",
    "this role",
    "career opportunities",
    "opportunities",
    "next steps for your job application",
}


suspicious_fragments = [
    "thank you for",
    "thanks for",
    "your application",
    "application received",
    "next steps for",
    "joining our",
    "joining ",
    "position with",
    "position at",
    "intern at ",
    "intern - ",
    "internship at ",
    "software engineer",
    "data engineer",
    "data analyst",
    "data scientist",
    "cybersecurity analyst",
    "ai engineer",
    "fullstack",
    "full-stack",
    "career opportunities",
    "regards to next steps",
    "working at ",
]


job_like_terms = [
    "engineer",
    "analyst",
    "scientist",
    "intern",
    "internship",
    "developer",
    "manager",
    "associate",
    "programmer",
]


# --------------------------------------------------
# DETECT SUSPICIOUS VALUES
# --------------------------------------------------

suspicious_records = []

for record in records:

    company = record["company_name"].strip()

    if not company:
        continue

    company_lower = company.lower()

    reasons = []

    if company_lower in suspicious_exact:
        reasons.append("SUSPICIOUS_EXACT")

    if any(
        fragment in company_lower
        for fragment in suspicious_fragments
    ):
        reasons.append("SUSPICIOUS_FRAGMENT")

    # Long company values may actually be prose/title text.
    if len(company.split()) > 10:
        reasons.append("VERY_LONG")

    # Detect job-title-looking values.
    job_term_count = sum(
        1
        for term in job_like_terms
        if term in company_lower
    )

    if job_term_count >= 2:
        reasons.append("JOB_TITLE_LIKE")

    if reasons:
        suspicious_records.append({
            **record,
            "suspicion_reason": "|".join(
                sorted(set(reasons))
            )
        })


# --------------------------------------------------
# COMPANY FREQUENCIES
# --------------------------------------------------

company_counts = Counter(
    record["company_name"].strip()
    for record in records
    if record["company_name"].strip()
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

    present_companies = [
        record
        for record in records
        if record["company_name"].strip()
    ]

    missing_companies = [
        record
        for record in records
        if not record["company_name"].strip()
    ]

    output.write(
        f"Companies present: {len(present_companies)}\n"
    )

    output.write(
        f"Missing companies: {len(missing_companies)}\n"
    )

    output.write(
        f"Suspicious company values: "
        f"{len(suspicious_records)}\n"
    )


    output.write(
        "\n=== MOST COMMON COMPANY VALUES ===\n"
    )

    for company, count in company_counts.most_common(50):
        output.write(
            f"{count:>3} | {company}\n"
        )


    output.write(
        "\n=== SUSPICIOUS COMPANY VALUES ===\n"
    )

    for record in suspicious_records:

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
            f"Company Source: "
            f"{record.get('company_source', '')}\n"
        )

        output.write(
            f"Reason: {record['suspicion_reason']}\n"
        )

        output.write(
            f"Job Title: {record['job_title']}\n"
        )

        output.write(
            f"Subject: {record['subject']}\n"
        )

        output.write(
            f"Sender: {record['sender']}\n"
        )


print(f"Total job-related emails: {len(records)}")
print(
    f"Companies present: "
    f"{sum(bool(r['company_name'].strip()) for r in records)}"
)
print(
    f"Missing companies: "
    f"{sum(not bool(r['company_name'].strip()) for r in records)}"
)
print(
    f"Suspicious company values: "
    f"{len(suspicious_records)}"
)

print(f"\nCreated: {OUTPUT_FILE}")