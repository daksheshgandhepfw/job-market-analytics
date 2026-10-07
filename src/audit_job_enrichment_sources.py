import pandas as pd
from pathlib import Path


# --------------------------------------------------
# Candidate source files
# --------------------------------------------------

SOURCE_FILES = [
    Path("data/processed/final_enriched_job_emails.csv"),
    Path("data/processed/enriched_job_emails.csv"),
    Path("data/processed/enriched_job_emails_with_titles.csv"),
    Path("data/processed/enriched_job_emails_with_body_titles.csv"),
    Path("data/processed/enriched_job_reference_ids.csv"),
    Path("data/processed/applications_deduplicated.csv"),
]


# --------------------------------------------------
# Inspect files
# --------------------------------------------------

print("=== JOB ENRICHMENT SOURCE AUDIT ===")

for file_path in SOURCE_FILES:

    print()
    print("=" * 70)
    print(f"FILE: {file_path}")
    print("=" * 70)

    if not file_path.exists():
        print("FILE NOT FOUND")
        continue

    df = pd.read_csv(file_path)

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print()
    print("--- COLUMNS ---")

    for column in df.columns:
        print(f"- {column}")

# --------------------------------------------------
# Inspect final enriched email content
# --------------------------------------------------

FINAL_EMAIL_FILE = Path(
    "data/processed/final_enriched_job_emails.csv"
)

emails = pd.read_csv(FINAL_EMAIL_FILE)

print()
print("=" * 70)
print("EMAIL CONTENT AUDIT")
print("=" * 70)

print()
print("--- EMAIL TYPE DISTRIBUTION ---")
print(
    emails["email_type"]
    .value_counts(dropna=False)
    .to_string()
)

print()
print("--- EMAIL BODY COMPLETENESS ---")

body_present = emails["email_body"].notna().sum()
body_missing = emails["email_body"].isna().sum()

print(f"Email body present: {body_present}")
print(f"Email body missing: {body_missing}")

print()
print("--- EMAIL BODY LENGTH ---")

body_lengths = (
    emails["email_body"]
    .fillna("")
    .astype(str)
    .str.len()
)

print(f"Minimum length: {body_lengths.min()}")
print(f"Median length: {body_lengths.median():.0f}")
print(f"Mean length: {body_lengths.mean():.0f}")
print(f"Maximum length: {body_lengths.max()}")

print()
print("--- EMAIL TYPE BODY LENGTH ---")

email_type_body_length = (
    emails
    .assign(body_length=body_lengths)
    .groupby("email_type")["body_length"]
    .agg(["count", "median", "mean", "max"])
    .round(1)
)

print(email_type_body_length.to_string())

# --------------------------------------------------
# Sample email bodies for content inspection
# --------------------------------------------------

print()
print("=" * 70)
print("EMAIL BODY SAMPLE")
print("=" * 70)

sample_columns = [
    "email_id",
    "email_type",
    "company_name",
    "job_title",
    "subject",
    "email_body"
]

confirmation_samples = (
    emails[
        emails["email_type"] == "Application Confirmation"
    ]
    .sample(
        n=min(10, (
            emails["email_type"] == "Application Confirmation"
        ).sum()),
        random_state=42
    )
)

rejection_samples = (
    emails[
        emails["email_type"] == "Rejection"
    ]
    .sample(
        n=min(5, (
            emails["email_type"] == "Rejection"
        ).sum()),
        random_state=42
    )
)

email_samples = pd.concat(
    [
        confirmation_samples,
        rejection_samples
    ]
)

for _, row in email_samples[sample_columns].iterrows():

    print()
    print("-" * 70)

    print(f"EMAIL ID: {row['email_id']}")
    print(f"TYPE: {row['email_type']}")
    print(f"COMPANY: {row['company_name']}")
    print(f"JOB TITLE: {row['job_title']}")
    print(f"SUBJECT: {row['subject']}")

    print()
    print("BODY:")
    print(str(row["email_body"])[:2000])