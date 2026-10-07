import csv
from collections import Counter
with open(
    "data/raw/application_emails.csv",
    "r",
    encoding="utf-8"
) as csv_file:
    reader = csv.DictReader(csv_file)
    records = list(reader)

print("Total emails:", len(records))

missing_company = 0

for record in records:
    if not record["company_name"]:
        missing_company += 1

print("Missing company names:", missing_company)

missing_job_title = 0

for record in records:
    if not record["job_title"]:
        missing_job_title += 1

print("Missing job titles:", missing_job_title)

email_type_counts = {}

for record in records:
    email_type = record["email_type"]

    if email_type not in email_type_counts:
        email_type_counts[email_type] = 0

    email_type_counts[email_type] += 1

print("Email type counts:")

for email_type, count in email_type_counts.items():
    print(f"  {email_type}: {count}")

print("\nOther email subjects:")

for record in records:
    if record["email_type"] == "Other":
        print("-", record["subject"])

other_records = []

for record in records:
    if record["email_type"] == "Other":
        other_records.append(record)

with open(
    "data/processed/other_emails_review.csv",
    "w",
    newline="",
    encoding="utf-8"
) as csv_file:
    writer = csv.DictWriter(
        csv_file,
        fieldnames=records[0].keys()
    )

    writer.writeheader()
    writer.writerows(other_records)

print(
    "\nSaved",
    len(other_records),
    "Other emails to data/processed/other_emails_review.csv"
)

print("\nMissing company/title review:")

for record in records:
    if not record["company_name"] or not record["job_title"]:
        print("\nSubject:", record["subject"])
        print("Company:", record["company_name"])
        print("Job title:", record["job_title"])
        print("Body preview:", record["email_body"][:300])
        print("-" * 50)

print("\nJob title review:")

for record in records:
    print(
        record["job_title"] if record["job_title"] else "MISSING",
        "|",
        record["subject"]
    )

for record in records:
    if not record["job_title"]:
        print("\nSubject:", record["subject"])
        print("Job title: MISSING")
        print("Body preview:", record["email_body"][:300])
        print("-" * 50)

print("\nMissing company review:")

for record in records:
    if not record["company_name"]:
        print("\nSubject:", record["subject"])
        print("Sender:", record["sender"])
        print("Job title:", record["job_title"])
        print("Body preview:", record["email_body"][:300])
        print("-" * 50)

print("\nCompany extraction review:")

for record in records:
    print(
        record["company_name"],
        "|",
        record["subject"]
    )

from collections import Counter

print("\n=== OTHER EMAIL PATTERN ANALYSIS ===")

other_records = [
    record
    for record in records
    if record["email_type"] == "Other"
]

print("Total Other emails:", len(other_records))


# --------------------------------------------------
# MOST COMMON SUBJECTS
# --------------------------------------------------

subject_counts = Counter(
    record["subject"].strip()
    for record in other_records
    if record["subject"].strip()
)

print("\nTop 30 Other email subjects:")

for subject, count in subject_counts.most_common(30):
    print(
        count,
        "|",
        subject
    )


# --------------------------------------------------
# MOST COMMON SENDERS
# --------------------------------------------------

sender_counts = Counter(
    record["sender"].strip()
    for record in other_records
    if record["sender"].strip()
)

print("\nTop 30 Other email senders:")

for sender, count in sender_counts.most_common(30):
    print(
        count,
        "|",
        sender
    )


# --------------------------------------------------
# COMPANY COMPLETENESS WITHIN OTHER EMAILS
# --------------------------------------------------

other_missing_company = sum(
    1
    for record in other_records
    if not record["company_name"].strip()
)

other_missing_title = sum(
    1
    for record in other_records
    if not record["job_title"].strip()
)

print("\nOther email data quality:")
print(
    "Missing company:",
    other_missing_company,
    "/",
    len(other_records)
)

print(
    "Missing job title:",
    other_missing_title,
    "/",
    len(other_records)
)

print("\n=== CLASSIFICATION VALIDATION ===")


# --------------------------------------------------
# APPLICATION CONFIRMATIONS
# --------------------------------------------------

confirmation_records = [
    record
    for record in records
    if record["email_type"] == "Application Confirmation"
]

print(
    "\nTotal Application Confirmations:",
    len(confirmation_records)
)

confirmation_subject_counts = Counter(
    record["subject"].strip()
    for record in confirmation_records
    if record["subject"].strip()
)

print("\nTop 30 Application Confirmation subjects:")

for subject, count in confirmation_subject_counts.most_common(30):
    print(
        count,
        "|",
        subject
    )


# --------------------------------------------------
# REJECTIONS
# --------------------------------------------------

rejection_records = [
    record
    for record in records
    if record["email_type"] == "Rejection"
]

print(
    "\nTotal Rejections:",
    len(rejection_records)
)

rejection_subject_counts = Counter(
    record["subject"].strip()
    for record in rejection_records
    if record["subject"].strip()
)

print("\nTop 30 Rejection subjects:")

for subject, count in rejection_subject_counts.most_common(30):
    print(
        count,
        "|",
        subject
    )


# --------------------------------------------------
# POSSIBLE SUSPICIOUS CONFIRMATIONS
# --------------------------------------------------

suspicious_terms = [
    "webinar",
    "talent community",
    "daily digest",
    "newsletter",
    "event",
    "register today",
    "admissions"
]

suspicious_confirmations = []

for record in confirmation_records:

    text = (
        record["subject"]
        + " "
        + record["email_body"]
    ).lower()

    if any(
        term in text
        for term in suspicious_terms
    ):
        suspicious_confirmations.append(record)


print(
    "\nPotentially suspicious confirmations:",
    len(suspicious_confirmations)
)

for record in suspicious_confirmations:
    print(
        record["email_id"],
        "|",
        record["sender"],
        "|",
        record["subject"]
    )

print("\n=== REJECTION RULE VALIDATION ===")


rejection_phrases = [
    "will not be moving ahead",
    "will not be moving forward",
    "not be moving forward",
    "decided not to move forward",
    "decided to not move forward",
    "decision to not move forward",
    "not selected",
    "not been selected",
    "other candidates",
    "decided to pursue another candidate",
    "unable to proceed with your application",
    "identified candidates whose skills and backgrounds more closely match",
    "this position has been filled",
    "decided to move forward with candidates whose qualification",
    "decided not to proceed further with your candidacy",
    "decided not to proceed with your candidacy",
    "not been selected as the best match"
]


rejection_records = [
    record
    for record in records
    if record["email_type"] == "Rejection"
]


print(
    "Total rejection emails:",
    len(rejection_records)
)


for record in rejection_records:

    text = (
        record["subject"]
        + " "
        + record["email_body"]
    ).lower()

    matched_phrases = [
        phrase
        for phrase in rejection_phrases
        if phrase in text
    ]

    print("\n----------------------------------------")
    print("Email ID:", record["email_id"])
    print("Company:", record["company_name"])
    print("Subject:", record["subject"])

    print(
        "Matched rejection phrase(s):",
        " | ".join(matched_phrases)
        if matched_phrases
        else "NONE"
    )

print("\n=== WEAK REJECTION SIGNAL REVIEW ===")

strong_rejection_phrases = [
    "will not be moving ahead",
    "will not be moving forward",
    "not be moving forward",
    "decided not to move forward",
    "decided to not move forward",
    "decision to not move forward",
    "decided to pursue another candidate",
    "unable to proceed with your application",
    "identified candidates whose skills and backgrounds more closely match",
    "this position has been filled",
    "decided to move forward with candidates whose qualification",
    "decided not to proceed further with your candidacy",
    "decided not to proceed with your candidacy",
    "not been selected as the best match"
]

weak_rejection_phrases = [
    "not selected",
    "not been selected",
    "other candidates"
]


weak_only_records = []


for record in rejection_records:

    text = (
        record["subject"]
        + " "
        + record["email_body"]
    ).lower()

    strong_matches = [
        phrase
        for phrase in strong_rejection_phrases
        if phrase in text
    ]

    weak_matches = [
        phrase
        for phrase in weak_rejection_phrases
        if phrase in text
    ]

    # Only review emails where:
    # - a weak rejection phrase exists
    # - NO strong rejection phrase exists
    if weak_matches and not strong_matches:

        weak_only_records.append(
            {
                "email_id": record["email_id"],
                "company_name": record["company_name"],
                "subject": record["subject"],
                "weak_matches": weak_matches
            }
        )


print(
    "Weak-signal-only rejections:",
    len(weak_only_records)
)


for record in weak_only_records:

    print("\n----------------------------------------")

    print(
        "Email ID:",
        record["email_id"]
    )

    print(
        "Company:",
        record["company_name"]
    )

    print(
        "Subject:",
        record["subject"]
    )

    print(
        "Weak phrase(s):",
        " | ".join(record["weak_matches"])
    )

print("\n=== WEAK REJECTION CONTEXT ===")

for record in rejection_records:

    text = (
        record["subject"]
        + " "
        + record["email_body"]
    )

    text_lower = text.lower()

    strong_matches = [
        phrase
        for phrase in strong_rejection_phrases
        if phrase in text_lower
    ]

    weak_matches = [
        phrase
        for phrase in weak_rejection_phrases
        if phrase in text_lower
    ]

    if not weak_matches or strong_matches:
        continue

    print("\n----------------------------------------")
    print("Email ID:", record["email_id"])
    print("Company:", record["company_name"])
    print("Subject:", record["subject"])

    for phrase in weak_matches:

        position = text_lower.find(phrase)

        start = max(
            0,
            position - 200
        )

        end = min(
            len(text),
            position + len(phrase) + 200
        )

        context = text[start:end]

        # Make output easier to read.
        context = " ".join(
            context.split()
        )

        print(
            f'\nContext around "{phrase}":'
        )

        print(context)