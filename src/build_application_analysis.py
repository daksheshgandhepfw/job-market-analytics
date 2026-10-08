from pathlib import Path

import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

APPLICATIONS_FILE = Path(
    "data/processed/applications.csv"
)

JOBS_FILE = Path(
    "data/processed/jobs_final.csv"
)

OUTPUT_FILE = Path(
    "data/processed/application_analysis.csv"
)


# --------------------------------------------------
# Load datasets
# --------------------------------------------------

applications = pd.read_csv(
    APPLICATIONS_FILE
)

jobs = pd.read_csv(
    JOBS_FILE
)


print("=== STAGE 5.1: BUILD APPLICATION ANALYSIS DATASET ===")
print()

print(
    f"Applications loaded: "
    f"{len(applications)}"
)

print(
    f"Jobs loaded: "
    f"{len(jobs)}"
)


# --------------------------------------------------
# Pre-join validation
# --------------------------------------------------

print()
print("--- PRE-JOIN VALIDATION ---")

print(
    f"Unique application IDs: "
    f"{applications['application_id'].nunique()}"
)

print(
    f"Duplicate application IDs: "
    f"{applications['application_id'].duplicated().sum()}"
)

print(
    f"Missing application job IDs: "
    f"{applications['job_id'].isna().sum()}"
)

print(
    f"Unique job IDs in jobs table: "
    f"{jobs['job_id'].nunique()}"
)

print(
    f"Duplicate job IDs in jobs table: "
    f"{jobs['job_id'].duplicated().sum()}"
)


# --------------------------------------------------
# Join applications to jobs
# --------------------------------------------------

application_analysis = applications.merge(
    jobs,
    on="job_id",
    how="left",
    validate="many_to_one"
)


# --------------------------------------------------
# Post-join validation
# --------------------------------------------------

print()
print("--- POST-JOIN VALIDATION ---")

print(
    f"Rows after join: "
    f"{len(application_analysis)}"
)

print(
    f"Unique application IDs: "
    f"{application_analysis['application_id'].nunique()}"
)

print(
    f"Duplicate application IDs: "
    f"{application_analysis['application_id'].duplicated().sum()}"
)


# --------------------------------------------------
# Check whether every application found a job
# --------------------------------------------------

unmatched_jobs = (
    application_analysis["company_name"]
    .isna()
    .sum()
)


print(
    f"Applications without matching job: "
    f"{unmatched_jobs}"
)


# --------------------------------------------------
# Select analytical columns
# --------------------------------------------------

application_analysis = application_analysis[
    [
        "application_id",
        "job_id",
        "company_name",
        "job_title",
        "job_title_clean",
        "role_category",
        "career_level",
        "job_reference_id",
        "application_date",
        "status",
        "response_status",
        "first_response_date",
        "email_count"
    ]
].copy()


# --------------------------------------------------
# Convert dates
# --------------------------------------------------

application_analysis["application_date"] = pd.to_datetime(
    application_analysis["application_date"],
    errors="coerce"
)

application_analysis["first_response_date"] = pd.to_datetime(
    application_analysis["first_response_date"],
    errors="coerce"
)


# --------------------------------------------------
# Dataset validation
# --------------------------------------------------

print()
print("--- DATASET VALIDATION ---")

print(
    f"Applications: "
    f"{len(application_analysis)}"
)

print(
    f"Unique application IDs: "
    f"{application_analysis['application_id'].nunique()}"
)

print(
    f"Missing application dates: "
    f"{application_analysis['application_date'].isna().sum()}"
)

print(
    f"Missing clean job titles: "
    f"{application_analysis['job_title_clean'].isna().sum()}"
)

print(
    f"Missing role categories: "
    f"{application_analysis['role_category'].isna().sum()}"
)

print(
    f"Missing career levels: "
    f"{application_analysis['career_level'].isna().sum()}"
)


# --------------------------------------------------
# Response validation
# --------------------------------------------------

print()
print("--- RESPONSE VALIDATION ---")

print(
    application_analysis["response_status"]
    .value_counts(dropna=False)
    .to_string()
)

print()

print(
    "Applications with first response date: "
    f"{application_analysis['first_response_date'].notna().sum()}"
)

print(
    "Applications without first response date: "
    f"{application_analysis['first_response_date'].isna().sum()}"
)


# --------------------------------------------------
# Save dataset
# --------------------------------------------------

application_analysis.to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print("=" * 70)
print("APPLICATION ANALYSIS DATASET CREATED")
print("=" * 70)

print(
    f"Saved to: "
    f"{OUTPUT_FILE}"
)


# --------------------------------------------------
# Post-save validation
# --------------------------------------------------

saved = pd.read_csv(
    OUTPUT_FILE
)


print()
print("--- POST-SAVE VALIDATION ---")

print(
    f"Saved rows: "
    f"{len(saved)}"
)

print(
    f"Unique application IDs: "
    f"{saved['application_id'].nunique()}"
)

print(
    f"Duplicate application IDs: "
    f"{saved['application_id'].duplicated().sum()}"
)

print(
    f"Columns: "
    f"{len(saved.columns)}"
)

print()
print(saved.columns.tolist())