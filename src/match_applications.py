import csv
from email.utils import parsedate_to_datetime

def create_match_key(record):
    company = record["company_name"].strip().lower()
    job_title = record["job_title"].strip().lower()
    reference_id = record["job_reference_id"].strip().lower()

    # Strongest identifier
    if reference_id:
        return f"REF::{reference_id}"

    # Second-best identifier
    if company and job_title:
        return f"COMPANY_TITLE::{company}::{job_title}"

    # Not enough information for automatic matching
    return None
from email.utils import parsedate_to_datetime


def derive_application_date(emails):
    """
    Use the earliest Application Confirmation email
    as the application date.

    If no confirmation exists, return None rather
    than guessing from another email type.
    """

    confirmation_dates = []

    for email in emails:
        if email["email_type"] == "Application Confirmation":
            email_date = parsedate_to_datetime(
                email["email_date"]
            )

            confirmation_dates.append(email_date)

    if not confirmation_dates:
        return None

    return min(confirmation_dates)

with open(
    "data/raw/application_emails.csv",
    "r",
    encoding="utf-8"
) as csv_file:
    reader = csv.DictReader(csv_file)
    records = list(reader)


print("Emails loaded:", len(records))

# Load manual application-matching decisions
review_decisions = {}

with open(
    "data/processed/application_matching_review.csv",
    "r",
    encoding="utf-8"
) as csv_file:
    reader = csv.DictReader(csv_file)

    for row in reader:
        review_decisions[row["email_id"]] = {
        "review_status": row["review_status"],
        "review_notes": row["review_notes"],
        "job_title": row["job_title"],
        "job_reference_id": row["job_reference_id"],
        "merge_target_email_id": row["merge_target_email_id"]

    }


print("Review decisions loaded:", len(review_decisions))

from collections import defaultdict


reference_groups = defaultdict(list)

for record in records:
    reference_id = record["job_reference_id"].strip()

    if reference_id:
        reference_groups[reference_id].append(record)


print("\nApplications with multiple emails matched by reference ID:")

for reference_id, emails in reference_groups.items():
    if len(emails) > 1:
        print(f"\nReference ID: {reference_id}")
        print("Number of emails:", len(emails))

        for email in emails:
            print(
                "-",
                email["company_name"],
                "|",
                email["job_title"] or "MISSING",
                "|",
                email["email_type"],
                "|",
                email["email_date"]
            )

company_title_groups = defaultdict(list)

for record in records:
    company = record["company_name"].strip().lower()
    job_title = record["job_title"].strip().lower()

    if company and job_title:
        key = (company, job_title)
        company_title_groups[key].append(record)


print("\nPotential matches by company + job title:")

for (company, job_title), emails in company_title_groups.items():
    if len(emails) > 1:

        # Skip groups already proven by the same reference ID
        reference_ids = {
            email["job_reference_id"].strip()
            for email in emails
            if email["job_reference_id"].strip()
        }

        # Rule 1 already handles records that share
        # the same non-empty reference ID.
        if len(reference_ids) == 1:
            continue

        # Different reference IDs prove that these
        # are different applications.
        if len(reference_ids) > 1:
            continue

        print(
            f"\n{company.title()} | {job_title}"
        )

        print("Number of emails:", len(emails))

        for email in emails:
            print(
                "-",
                email["email_type"],
                "|",
                email["job_reference_id"] or "MISSING",
                "|",
                email["email_date"]
            )

print("\nRecords needing application matching review:")

for record in records:
    company = record["company_name"].strip()
    job_title = record["job_title"].strip()
    reference_id = record["job_reference_id"].strip()

    if company and not job_title and not reference_id:
        print(
            company,
            "|",
            record["email_date"],
            "|",
            record["email_type"],
            "|",
            record["subject"]
        )
# review_records = []

# for record in records:
#     company = record["company_name"].strip()
#     job_title = record["job_title"].strip()
#     reference_id = record["job_reference_id"].strip()

#     if company and not job_title and not reference_id:
#         review_records.append({
#             "email_id": record["email_id"],
#             "company_name": company,
#             "job_title": job_title,
#             "job_reference_id": reference_id,
#             "email_date": record["email_date"],
#             "email_type": record["email_type"],
#             "subject": record["subject"],
#             "review_status": "Needs Review",
#             "review_notes": ""
#         })


# with open(
#     "data/processed/application_matching_review.csv",
#     "w",
#     newline="",
#     encoding="utf-8"
# ) as csv_file:

#     fieldnames = [
#         "email_id",
#         "company_name",
#         "job_title",
#         "job_reference_id",
#         "email_date",
#         "email_type",
#         "subject",
#         "review_status",
#         "review_notes"
#     ]

#     writer = csv.DictWriter(
#         csv_file,
#         fieldnames=fieldnames
#     )

#     writer.writeheader()
#     writer.writerows(review_records)


# print(
#     "\nSaved",
#     len(review_records),
#     "records to data/processed/application_matching_review.csv"
# )

print("\nSample application match keys:")

for record in records:
    match_key = create_match_key(record)

    print(
        record["company_name"],
        "|",
        record["job_title"] or "MISSING",
        "|",
        match_key or "REVIEW"
    )

unique_match_keys = set()
review_count = 0

for record in records:
    match_key = create_match_key(record)

    if match_key:
        unique_match_keys.add(match_key)
    else:
        review_count += 1


print("\nApplication candidate summary:")
print("Total emails:", len(records))
print("Unique automatic match keys:", len(unique_match_keys))
print("Emails requiring review:", review_count)

print("\nManual review decisions:")

for email_id, decision in review_decisions.items():
    print(
        email_id,
        "|",
        decision["review_status"],
        "|",
        decision["review_notes"]
    )

print("\n=== MANUAL INFO REVIEW ===")

manual_review_ids = {
    email_id
    for email_id, decision in review_decisions.items()
    if decision["review_status"] == "NEEDS_MANUAL_INFO"
}

for record in records:
    if record["email_id"] in manual_review_ids:
        print("\n------------------------------")
        print("Company:", record["company_name"])
        print("Date:", record["email_date"])
        print("Subject:", record["subject"])
        print("Email type:", record["email_type"])
        print("Job title:", record["job_title"] or "MISSING")
        print("Reference ID:", record["job_reference_id"] or "MISSING")
        print("\nBODY:")
        print(record["email_body"])

# --------------------------------------------------
# BUILD UNIQUE APPLICATION GROUPS
# --------------------------------------------------
records_by_email_id = {
    record["email_id"]: record
    for record in records
}

application_groups = defaultdict(list)

for record in records:
    email_id = record["email_id"]

    # Check whether this email went through manual review
    decision = review_decisions.get(email_id)

    if decision:
        review_status = decision["review_status"]

        # Not a real job application
        if review_status == "EXCLUDE_NOT_APPLICATION":
            continue

        # This email belongs to another application.
        # We will handle the merge separately.
        if review_status == "MERGE_WITH_OTHER_EMAIL":
            target_email_id = decision["merge_target_email_id"].strip()

            if not target_email_id:
                print(
                    "WARNING: Missing merge target for",
                    email_id
                )
                continue

            target_record = records_by_email_id.get(target_email_id)

            if not target_record:
                print(
                    "WARNING: Merge target not found:",
                    target_email_id
                )
                continue

            target_key = f"MANUAL::{target_email_id}"

            application_groups[target_key].append(record)

            continue

        # Manually confirmed application
        if review_status == "KEEP_AS_APPLICATION":

            # Use manually corrected values when available.
            corrected_title = decision["job_title"].strip()
            corrected_reference_id = decision["job_reference_id"].strip()

            if corrected_title:
                record["job_title"] = corrected_title

            if corrected_reference_id:
                record["job_reference_id"] = corrected_reference_id

            # If manual review recovered a reference ID,
            # use it as the strongest application key.
            if corrected_reference_id:
                key = f"REF::{corrected_reference_id.lower()}"
            else:
                key = f"MANUAL::{email_id}"

            application_groups[key].append(record)
            continue

    # Normal automatically matched record
    match_key = create_match_key(record)

    if match_key:
        application_groups[match_key].append(record)


print("\n=== UNIQUE APPLICATION GROUPS ===")
print("Unique applications:", len(application_groups))

for number, (key, emails) in enumerate(
    application_groups.items(),
    start=1
):
    application_id = f"APP{number:04d}"

    first_email = emails[0]

    print(
        application_id,
        "|",
        first_email["company_name"],
        "|",
        first_email["job_title"] or "MISSING",
        "|",
        len(emails),
        "email(s)"
    )

print("\n=== APPLICATION DATE REVIEW ===")

missing_application_dates = 0

for number, (key, emails) in enumerate(
    application_groups.items(),
    start=1
):
    application_id = f"APP{number:04d}"

    application_date = derive_application_date(emails)

    if application_date is None:
        missing_application_dates += 1
        date_display = "MISSING"
    else:
        date_display = application_date.date().isoformat()

    first_email = emails[0]

    print(
        application_id,
        "|",
        first_email["company_name"],
        "|",
        first_email["job_title"] or "MISSING",
        "|",
        date_display
    )


print(
    "\nApplications missing application date:",
    missing_application_dates
)