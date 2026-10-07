from pathlib import Path

import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

JOBS_FILE = Path(
    "data/processed/jobs_enriched.csv"
)

APPLICATIONS_FILE = Path(
    "data/processed/applications.csv"
)

EMAILS_FILE = Path(
    "data/processed/final_enriched_job_emails.csv"
)


# --------------------------------------------------
# Load datasets
# --------------------------------------------------

jobs = pd.read_csv(JOBS_FILE)

applications = pd.read_csv(
    APPLICATIONS_FILE
)

emails = pd.read_csv(
    EMAILS_FILE
)


print("=== STAGE 3.15: JOB LOCATION AVAILABILITY AUDIT ===")
print()

print(f"Jobs loaded: {len(jobs)}")
print(f"Applications loaded: {len(applications)}")
print(f"Emails loaded: {len(emails)}")


# --------------------------------------------------
# Expand application -> email relationships
# --------------------------------------------------

application_email_links = (
    applications[
        [
            "application_id",
            "job_id",
            "email_ids"
        ]
    ]
    .assign(
        email_id=lambda x:
        x["email_ids"].str.split("|")
    )
    .explode("email_id")
)

application_email_links["email_id"] = (
    application_email_links["email_id"]
    .str.strip()
)


# --------------------------------------------------
# Join email content
# --------------------------------------------------

location_audit = (
    application_email_links
    .merge(
        emails[
            [
                "email_id",
                "email_type",
                "subject",
                "email_body"
            ]
        ],
        on="email_id",
        how="left"
    )
    .merge(
        jobs[
            [
                "job_id",
                "company_name",
                "job_title"
            ]
        ],
        on="job_id",
        how="left"
    )
)


# --------------------------------------------------
# Validate email linkage
# --------------------------------------------------

print()
print("--- EMAIL LINKAGE ---")

print(
    f"Email links created: "
    f"{len(location_audit)}"
)

print(
    f"Email links matched: "
    f"{location_audit['email_body'].notna().sum()}"
)

print(
    f"Email links unmatched: "
    f"{location_audit['email_body'].isna().sum()}"
)

print(
    f"Jobs represented: "
    f"{location_audit['job_id'].nunique()}"
)


# --------------------------------------------------
# Basic location-language audit
# --------------------------------------------------

location_phrases = {
    "remote": r"\bremote\b",
    "hybrid": r"\bhybrid\b",
    "onsite": r"\bon[\s-]?site\b",
    "location": r"\blocation\b",
    "located": r"\blocated\b",
    "office": r"\boffice\b",
    "relocation": r"\brelocation\b",
}


email_bodies = (
    location_audit["email_body"]
    .fillna("")
    .astype(str)
)


print()
print("--- LOCATION LANGUAGE ---")

for label, pattern in location_phrases.items():

    count = (
        email_bodies
        .str.contains(
            pattern,
            case=False,
            regex=True
        )
        .sum()
    )

    print(
        f"{label}: {count}"
    )


# --------------------------------------------------
# Count jobs with any location-related language
# --------------------------------------------------

combined_pattern = (
    r"\bremote\b|"
    r"\bhybrid\b|"
    r"\bon[\s-]?site\b|"
    r"\blocation\b|"
    r"\blocated\b|"
    r"\boffice\b|"
    r"\brelocation\b"
)

location_audit["has_location_language"] = (
    email_bodies
    .str.contains(
        combined_pattern,
        case=False,
        regex=True
    )
)


jobs_with_location_language = (
    location_audit.loc[
        location_audit["has_location_language"],
        "job_id"
    ]
    .nunique()
)


print()
print("--- JOB-LEVEL COVERAGE ---")

print(
    f"Total jobs: "
    f"{jobs['job_id'].nunique()}"
)

print(
    f"Jobs with location-related email language: "
    f"{jobs_with_location_language}"
)

print(
    f"Jobs without location-related email language: "
    f"{jobs['job_id'].nunique() - jobs_with_location_language}"
)