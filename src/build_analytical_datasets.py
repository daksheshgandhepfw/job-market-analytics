import pandas as pd
from pathlib import Path


# --------------------------------------------------
# File paths
# --------------------------------------------------

INPUT_FILE = Path("data/processed/applications_deduplicated.csv")

JOBS_OUTPUT_FILE = Path("data/processed/jobs.csv")
APPLICATIONS_OUTPUT_FILE = Path("data/processed/applications.csv")


# --------------------------------------------------
# Load validated Stage 1 dataset
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)


# --------------------------------------------------
# Initial inspection
# --------------------------------------------------

print("=== STAGE 2: ANALYTICAL DATASET BUILD ===")
print()

print(f"Applications loaded: {len(df)}")

print()
print("--- COLUMNS ---")

for column in df.columns:
    print(f"- {column}")

print()
print("--- FIRST 5 ROWS ---")

print(df.head().to_string(index=False))

# --------------------------------------------------
# Normalize fields used for job matching
# --------------------------------------------------

def normalize_text(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "":
        return None

    return " ".join(value.lower().split())


df["company_name_normalized"] = df["company_name"].apply(normalize_text)
df["job_title_normalized"] = df["job_title"].apply(normalize_text)


# --------------------------------------------------
# Inspect job-identification coverage
# --------------------------------------------------

has_reference_id = df["job_reference_id"].notna()
has_job_title = df["job_title"].notna()

reference_id_jobs = has_reference_id.sum()

title_only_jobs = (
    ~has_reference_id
    & has_job_title
).sum()

ambiguous_jobs = (
    ~has_reference_id
    & ~has_job_title
).sum()


print()
print("=== JOB IDENTIFICATION COVERAGE ===")
print()

print(f"Applications with reference ID: {reference_id_jobs}")
print(f"Applications with title but no reference ID: {title_only_jobs}")
print(f"Applications with neither title nor reference ID: {ambiguous_jobs}")

print()
print(f"Total: {reference_id_jobs + title_only_jobs + ambiguous_jobs}")

# --------------------------------------------------
# Create temporary job identity key
# --------------------------------------------------

def create_job_key(row):

    company = row["company_name_normalized"]
    title = row["job_title_normalized"]
    reference_id = row["job_reference_id"]

    # Rule 1:
    # Reference ID available
    if pd.notna(reference_id):
        return f"REF|{company}|{str(reference_id).strip()}"

    # Rule 2:
    # No reference ID, but job title available
    if pd.notna(title):
        return f"TITLE|{company}|{title}"

    # Rule 3:
    # Neither reference ID nor title available
    # Keep each application as its own job
    return f"APP|{row['application_id']}"


df["job_key"] = df.apply(create_job_key, axis=1)


# --------------------------------------------------
# Inspect job-key results
# --------------------------------------------------

unique_job_count = df["job_key"].nunique()

duplicate_job_applications = df.duplicated(
    subset=["job_key"],
    keep=False
)

print()
print("=== JOB KEY RESULTS ===")
print()

print(f"Total applications: {len(df)}")
print(f"Unique job keys: {unique_job_count}")
print(
    f"Applications sharing a job key: "
    f"{duplicate_job_applications.sum()}"
)

print()
print("--- SHARED JOB KEYS ---")

shared_jobs = (
    df[duplicate_job_applications]
    .sort_values("job_key")
    [
        [
            "application_id",
            "company_name",
            "job_title",
            "job_reference_id",
            "job_key"
        ]
    ]
)

if len(shared_jobs) == 0:
    print("None")
else:
    print(shared_jobs.to_string(index=False))

# --------------------------------------------------
# Inspect repeated job applications
# --------------------------------------------------

print()
print("=== REPEATED JOB APPLICATION DETAILS ===")
print()

repeated_job_details = (
    df[duplicate_job_applications]
    .sort_values(["job_key", "application_date", "application_id"])
    [
        [
            "application_id",
            "company_name",
            "job_title",
            "job_reference_id",
            "application_date",
            "status",
            "response_status",
            "first_response_date",
            "email_count",
            "email_ids",
            "job_key"
        ]
    ]
)

print(repeated_job_details.to_string(index=False))

# --------------------------------------------------
# Assign unique job IDs
# --------------------------------------------------

unique_job_keys = df["job_key"].drop_duplicates().tolist()

job_id_map = {
    job_key: f"JOB{i:04d}"
    for i, job_key in enumerate(unique_job_keys, start=1)
}

df["job_id"] = df["job_key"].map(job_id_map)


# --------------------------------------------------
# Validate job ID assignment
# --------------------------------------------------

print()
print("=== JOB ID ASSIGNMENT ===")
print()

print(f"Total applications: {len(df)}")
print(f"Unique job keys: {df['job_key'].nunique()}")
print(f"Unique job IDs: {df['job_id'].nunique()}")
print(f"Missing job IDs: {df['job_id'].isna().sum()}")

print()
print("--- SAMPLE JOB ID ASSIGNMENTS ---")

print(
    df[
        [
            "application_id",
            "job_id",
            "company_name",
            "job_title",
            "job_reference_id"
        ]
    ]
    .head(10)
    .to_string(index=False)
)

# --------------------------------------------------
# Build jobs dataset
# --------------------------------------------------

jobs = (
    df[
        [
            "job_id",
            "company_name",
            "job_title",
            "job_reference_id"
        ]
    ]
    .drop_duplicates(subset=["job_id"])
    .reset_index(drop=True)
)


# --------------------------------------------------
# Build applications dataset
# --------------------------------------------------

applications = (
    df[
        [
            "application_id",
            "job_id",
            "application_date",
            "status",
            "response_status",
            "first_response_date",
            "email_count",
            "email_ids"
        ]
    ]
    .copy()
    .reset_index(drop=True)
)


# --------------------------------------------------
# Convert date columns
# --------------------------------------------------

applications["application_date"] = pd.to_datetime(
    applications["application_date"],
    errors="coerce"
)

applications["first_response_date"] = pd.to_datetime(
    applications["first_response_date"],
    errors="coerce"
)


# --------------------------------------------------
# Validate analytical datasets
# --------------------------------------------------

print()
print("=== ANALYTICAL DATASET VALIDATION ===")
print()

print(f"Jobs: {len(jobs)}")
print(f"Applications: {len(applications)}")

print()
print("--- JOBS ---")
print(f"Unique job IDs: {jobs['job_id'].nunique()}")
print(f"Duplicate job IDs: {jobs['job_id'].duplicated().sum()}")
print(f"Missing job IDs: {jobs['job_id'].isna().sum()}")

print()
print("--- APPLICATIONS ---")
print(f"Unique application IDs: {applications['application_id'].nunique()}")
print(
    f"Duplicate application IDs: "
    f"{applications['application_id'].duplicated().sum()}"
)
print(f"Missing job IDs: {applications['job_id'].isna().sum()}")


# --------------------------------------------------
# Validate relationship between datasets
# --------------------------------------------------

orphan_job_ids = (
    set(applications["job_id"])
    - set(jobs["job_id"])
)

print()
print("--- RELATIONSHIP ---")
print(f"Orphan job IDs: {len(orphan_job_ids)}")


# --------------------------------------------------
# Application count per job
# --------------------------------------------------

applications_per_job = (
    applications
    .groupby("job_id")
    .size()
)

print()
print("--- APPLICATIONS PER JOB ---")
print(f"Jobs with 1 application: {(applications_per_job == 1).sum()}")
print(f"Jobs with 2+ applications: {(applications_per_job >= 2).sum()}")
print(f"Maximum applications for one job: {applications_per_job.max()}")

# --------------------------------------------------
# Final quality inspection
# --------------------------------------------------

print()
print("=== FINAL QUALITY INSPECTION ===")

print()
print("--- JOBS MISSING VALUES ---")
print(jobs.isna().sum().to_string())

print()
print("--- APPLICATIONS MISSING VALUES ---")
print(applications.isna().sum().to_string())

print()
print("--- JOBS DATA TYPES ---")
print(jobs.dtypes.to_string())

print()
print("--- APPLICATIONS DATA TYPES ---")
print(applications.dtypes.to_string())

print()
print("--- JOBS SAMPLE ---")
print(jobs.head(10).to_string(index=False))

print()
print("--- APPLICATIONS SAMPLE ---")
print(applications.head(10).to_string(index=False))

# --------------------------------------------------
# Save final analytical datasets
# --------------------------------------------------

jobs.to_csv(
    JOBS_OUTPUT_FILE,
    index=False
)

applications.to_csv(
    APPLICATIONS_OUTPUT_FILE,
    index=False,
    date_format="%Y-%m-%d"
)


print()
print("=== FILES SAVED ===")
print()
print(f"Jobs saved to: {JOBS_OUTPUT_FILE}")
print(f"Applications saved to: {APPLICATIONS_OUTPUT_FILE}")

# --------------------------------------------------
# Post-save validation
# --------------------------------------------------

saved_jobs = pd.read_csv(JOBS_OUTPUT_FILE)
saved_applications = pd.read_csv(APPLICATIONS_OUTPUT_FILE)

print()
print("=== POST-SAVE VALIDATION ===")
print()

print(f"Saved jobs: {len(saved_jobs)}")
print(f"Saved applications: {len(saved_applications)}")

print()
print("--- ID VALIDATION ---")
print(f"Unique saved job IDs: {saved_jobs['job_id'].nunique()}")
print(
    f"Unique saved application IDs: "
    f"{saved_applications['application_id'].nunique()}"
)

print()
print("--- DUPLICATE VALIDATION ---")
print(
    f"Duplicate saved job IDs: "
    f"{saved_jobs['job_id'].duplicated().sum()}"
)
print(
    f"Duplicate saved application IDs: "
    f"{saved_applications['application_id'].duplicated().sum()}"
)

print()
print("--- RELATIONSHIP VALIDATION ---")

saved_orphan_job_ids = (
    set(saved_applications["job_id"])
    - set(saved_jobs["job_id"])
)

print(f"Orphan job IDs: {len(saved_orphan_job_ids)}")

print()
print("--- REQUIRED FIELD VALIDATION ---")
print(f"Jobs missing job_id: {saved_jobs['job_id'].isna().sum()}")
print(
    f"Applications missing application_id: "
    f"{saved_applications['application_id'].isna().sum()}"
)
print(
    f"Applications missing job_id: "
    f"{saved_applications['job_id'].isna().sum()}"
)