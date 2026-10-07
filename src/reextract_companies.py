import csv

from extract_gmail import (
    extract_company_name,
    extract_company_name_from_subject,
    extract_company_from_known_sender,
    extract_company_name_from_sender
)


INPUT_FILE = "data/raw/application_emails.csv"
RELEVANCE_FILE = "data/processed/final_email_relevance.csv"
OUTPUT_FILE = "data/processed/company_reextraction_test.csv"


# --------------------------------------------------
# LOAD JOB-RELATED EMAIL IDS
# --------------------------------------------------

job_email_ids = set()

with open(RELEVANCE_FILE, "r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)

    for record in reader:
        if record["final_relevance"] == "JOB_RELATED":
            job_email_ids.add(record["email_id"])


# --------------------------------------------------
# RE-EXTRACT COMPANY NAMES
# --------------------------------------------------

records = []

with open(INPUT_FILE, "r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)

    for record in reader:

        # Only evaluate emails confirmed as job-related.
        if record["email_id"] not in job_email_ids:
            continue

        old_company = record["company_name"].strip()

        # Re-run extraction locally using already-stored data.
        body_company = extract_company_name(
            record["email_body"]
        )

        subject_company = extract_company_name_from_subject(
            record["subject"]
        )

        known_sender_company = extract_company_from_known_sender(
            record["sender"]
        )

        sender_company = extract_company_name_from_sender(
            record["sender"]
        )

        # Priority:
        # existing -> subject -> known sender -> sender display -> body
        if old_company:
            new_company = old_company
            extraction_source = "EXISTING"

        elif subject_company:
            new_company = subject_company
            extraction_source = "SUBJECT"

        elif known_sender_company:
            new_company = known_sender_company
            extraction_source = "KNOWN_SENDER"

        elif sender_company:
            new_company = sender_company
            extraction_source = "SENDER"

        elif body_company:
            new_company = body_company
            extraction_source = "BODY"

        else:
            new_company = ""
            extraction_source = "MISSING"

        records.append({
            "email_id": record["email_id"],
            "subject": record["subject"],
            "sender": record["sender"],
            "old_company_name": old_company,
            "new_company_name": new_company,
            "extraction_source": extraction_source
        })


# --------------------------------------------------
# SAVE TEST OUTPUT
# --------------------------------------------------

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as csv_file:

    fieldnames = [
        "email_id",
        "subject",
        "sender",
        "old_company_name",
        "new_company_name",
        "extraction_source"
    ]

    writer = csv.DictWriter(
        csv_file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(records)


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

old_missing = sum(
    1 for record in records
    if not record["old_company_name"]
)

new_missing = sum(
    1 for record in records
    if not record["new_company_name"]
)

recovered = sum(
    1 for record in records
    if (
        not record["old_company_name"]
        and record["new_company_name"]
    )
)


print(f"Total job-related emails: {len(records)}")
print(f"Old missing companies: {old_missing}")
print(f"New missing companies: {new_missing}")
print(f"Companies recovered: {recovered}")


# --------------------------------------------------
# RECOVERY SOURCE COUNTS
# --------------------------------------------------

print("\nRecovery source counts:")

source_counts = {}

for record in records:
    source = record["extraction_source"]

    source_counts[source] = (
        source_counts.get(source, 0) + 1
    )

for source, count in source_counts.items():
    print(f"{source}: {count}")


print(f"\nCreated: {OUTPUT_FILE}")


# --------------------------------------------------
# RECOVERED COMPANY AUDIT
# --------------------------------------------------

print("\n=== RECOVERED COMPANIES ===")

for record in records:

    if (
        not record["old_company_name"]
        and record["new_company_name"]
    ):
        print("\n----------------------------------------")
        print("Email ID:", record["email_id"])
        print("Subject:", record["subject"])
        print("Sender:", record["sender"])
        print(
            "Recovered Company:",
            record["new_company_name"]
        )
        print(
            "Source:",
            record["extraction_source"]
        )


# --------------------------------------------------
# STILL-MISSING COMPANY AUDIT
# --------------------------------------------------

print("\n=== STILL MISSING COMPANIES ===")

for record in records:

    if not record["new_company_name"]:
        print("\n----------------------------------------")
        print("Email ID:", record["email_id"])
        print("Subject:", record["subject"])
        print("Sender:", record["sender"])