import csv
from collections import Counter

from extract_gmail import classify_email


INPUT_FILE = "data/raw/application_emails.csv"


# --------------------------------------------------
# LOAD EXISTING EMAIL DATA
# --------------------------------------------------

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as csv_file:

    reader = csv.DictReader(csv_file)
    records = list(reader)


print("Emails loaded:", len(records))


# --------------------------------------------------
# STORE OLD COUNTS
# --------------------------------------------------

old_counts = Counter(
    record["email_type"]
    for record in records
)


# --------------------------------------------------
# RECLASSIFY
# --------------------------------------------------

changed_count = 0

for record in records:

    old_type = record["email_type"]

    new_type = classify_email(
        record["email_body"],
        record["subject"]
    )

    if old_type != new_type:
        changed_count += 1

    record["email_type"] = new_type


# --------------------------------------------------
# CALCULATE NEW COUNTS
# --------------------------------------------------

new_counts = Counter(
    record["email_type"]
    for record in records
)


# --------------------------------------------------
# SAVE UPDATED DATA
# --------------------------------------------------

fieldnames = records[0].keys()

with open(
    INPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as csv_file:

    writer = csv.DictWriter(
        csv_file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(records)


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

print("\nClassification changes:", changed_count)

print("\nBefore:")
for email_type, count in old_counts.items():
    print(
        f"  {email_type}: {count}"
    )

print("\nAfter:")
for email_type, count in new_counts.items():
    print(
        f"  {email_type}: {count}"
    )

print(
    "\nUpdated:",
    INPUT_FILE
)