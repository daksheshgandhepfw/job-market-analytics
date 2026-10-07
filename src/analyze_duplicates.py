import csv
from collections import Counter


with open(
    "data/raw/application_emails.csv",
    "r",
    encoding="utf-8"
) as csv_file:
    reader = csv.DictReader(csv_file)
    records = list(reader)


print("Total email records:", len(records))


companies = [
    record["company_name"]
    for record in records
    if record["company_name"]
]


company_counts = Counter(companies)


print("\nCompanies with multiple emails:")

for company, count in company_counts.most_common():
    if count > 1:
        print(company, "|", count)

print("\nDetailed review of companies with multiple emails:")

for company, count in company_counts.most_common():
    if count <= 1:
        continue

    print(f"\n--- {company} ({count} emails) ---")

    for record in records:
        if record["company_name"] == company:
            print("Job title:", record["job_title"] or "MISSING")
            print(
                "Reference ID:",
                record["job_reference_id"] or "MISSING"
            )
            print("Email date:", record["email_date"])
            print("Email type:", record["email_type"])
            print("Subject:", record["subject"])
            print()