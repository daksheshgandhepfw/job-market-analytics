import csv
from collections import Counter


INPUT_FILE = "data/raw/application_emails.csv"


with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as csv_file:

    reader = csv.DictReader(csv_file)
    records = list(reader)


print("=== JOB RELEVANCE AUDIT ===")
print("Total emails:", len(records))


# --------------------------------------------------
# SUBJECT ANALYSIS
# --------------------------------------------------

subject_counts = Counter(
    record["subject"].strip()
    for record in records
)


print("\n=== MOST COMMON SUBJECTS ===")

for subject, count in subject_counts.most_common(30):
    print(f"{count:>3} | {subject}")


# --------------------------------------------------
# SENDER ANALYSIS
# --------------------------------------------------

sender_counts = Counter(
    record["sender"].strip()
    for record in records
)


print("\n=== MOST COMMON SENDERS ===")

for sender, count in sender_counts.most_common(30):
    print(f"{count:>3} | {sender}")


# --------------------------------------------------
# POTENTIAL NON-JOB EMAILS
# --------------------------------------------------

non_job_terms = [
    "admission",
    "admissions",
    "graduate school",
    "graduate studies",
    "degree program",
    "university applicant",
    "international applicant",
    "webinar",
    "student application",
    "talent community",
    "daily digest",
    "activate account",
    "borderpass"
]


potential_non_job_records = []


for record in records:

    text = (
        record["subject"]
        + " "
        + record["sender"]
        + " "
        + record["email_body"]
    ).lower()

    matched_terms = [
        term
        for term in non_job_terms
        if term in text
    ]

    if matched_terms:

        potential_non_job_records.append(
            {
                "email_id": record["email_id"],
                "subject": record["subject"],
                "sender": record["sender"],
                "email_type": record["email_type"],
                "matched_terms": matched_terms
            }
        )


print("\n=== POTENTIAL NON-JOB EMAILS ===")

print(
    "Potential non-job emails:",
    len(potential_non_job_records)
)


for record in potential_non_job_records:

    print("\n----------------------------------------")

    print(
        "Email ID:",
        record["email_id"]
    )

    print(
        "Subject:",
        record["subject"]
    )

    print(
        "Sender:",
        record["sender"]
    )

    print(
        "Email Type:",
        record["email_type"]
    )

    print(
        "Matched term(s):",
        " | ".join(record["matched_terms"])
    )