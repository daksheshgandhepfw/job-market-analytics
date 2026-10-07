import csv
from collections import Counter


RAW_EMAIL_FILE = "data/raw/application_emails.csv"
RELEVANCE_FILE = "data/processed/final_email_relevance.csv"


# --------------------------------------------------
# LOAD FINAL JOB-RELATED EMAIL IDS
# --------------------------------------------------

job_email_ids = set()

with open(
    RELEVANCE_FILE,
    "r",
    encoding="utf-8"
) as csv_file:

    reader = csv.DictReader(csv_file)

    for record in reader:
        if record["final_relevance"] == "JOB_RELATED":
            job_email_ids.add(record["email_id"])


# --------------------------------------------------
# LOAD JOB-RELATED RAW EMAILS
# --------------------------------------------------

job_records = []

with open(
    RAW_EMAIL_FILE,
    "r",
    encoding="utf-8"
) as csv_file:

    reader = csv.DictReader(csv_file)

    for record in reader:
        if record["email_id"] in job_email_ids:
            job_records.append(record)


# --------------------------------------------------
# DATA QUALITY METRICS
# --------------------------------------------------

missing_company = [
    record
    for record in job_records
    if not record["company_name"].strip()
]

missing_title = [
    record
    for record in job_records
    if not record["job_title"].strip()
]

missing_both = [
    record
    for record in job_records
    if (
        not record["company_name"].strip()
        and not record["job_title"].strip()
    )
]


print(f"Job-related emails: {len(job_records)}")

print(
    f"Missing company names: "
    f"{len(missing_company)}"
)

print(
    f"Missing job titles: "
    f"{len(missing_title)}"
)

print(
    f"Missing both company and title: "
    f"{len(missing_both)}"
)


# --------------------------------------------------
# MOST COMMON EXTRACTED COMPANIES
# --------------------------------------------------

company_counts = Counter(
    record["company_name"]
    for record in job_records
    if record["company_name"].strip()
)

print("\n=== MOST COMMON EXTRACTED COMPANIES ===")

for company, count in company_counts.most_common(30):
    print(f"{count:>3} | {company}")


# --------------------------------------------------
# MOST COMMON EXTRACTED JOB TITLES
# --------------------------------------------------

title_counts = Counter(
    record["job_title"]
    for record in job_records
    if record["job_title"].strip()
)

print("\n=== MOST COMMON EXTRACTED JOB TITLES ===")

for title, count in title_counts.most_common(30):
    print(f"{count:>3} | {title}")


# --------------------------------------------------
# SAMPLE MISSING COMPANY
# --------------------------------------------------

print("\n=== SAMPLE: MISSING COMPANY ===")

for record in missing_company:
    print("\n----------------------------------------")
    print("Email ID:", record["email_id"])
    print("Subject:", record["subject"])
    print("Sender:", record["sender"])
    print("Job Title:", record["job_title"])


# --------------------------------------------------
# SAMPLE MISSING JOB TITLE
# --------------------------------------------------

print("\n=== SAMPLE: MISSING JOB TITLE ===")

for record in missing_title[:30]:
    print("\n----------------------------------------")
    print("Email ID:", record["email_id"])
    print("Subject:", record["subject"])
    print("Sender:", record["sender"])
    print("Company:", record["company_name"])