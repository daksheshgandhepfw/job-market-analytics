from pathlib import Path

import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

JOBS_FILE = Path(
    "data/processed/jobs.csv"
)

JOBS_ENRICHED_FILE = Path(
    "data/processed/jobs.csv"
)

RECOVERY_AUDIT_FILE = Path(
    "data/processed/job_title_recovery_audit.csv"
)


# --------------------------------------------------
# Titles manually verified from source email evidence
# --------------------------------------------------

verified_titles = {
    "JOB0057": "Eli Lilly Business Insights & Analytics Data Engineering Intern",
    "JOB0074": "Associate AI Engineer",
    "JOB0101": "Data Infra Engineer",
    "JOB0109": "Associate Data Analyst-Retail",
    "JOB0114": "Data Engineer, JR",
    "JOB0119": "Eli Lilly Technology Data Engineer - Intern to FTE",
    "JOB0121": "Data Engineer Intern",
    "JOB0125": "Eli Lilly AI Data Engineering Intern (BS)",
    "JOB0138": "Entry Level Data Backend Engineer - Trust & Safety (Remote - Canada)",
    "JOB0143": "Junior Software Engineer (Remote)",
    "JOB0158": "Software Engineer I",
    "JOB0177": "Software Engineer I",
    "JOB0195": "Computing Graduate Student Intern - Spring 2027",
    "JOB0220": "Business Intelligence Analyst",
    "JOB0249": "Associate Data Engineer (CollegeGrad 2027)",
    "JOB0280": "Program Analyst",
    "JOB0281": "Software Engineer I, Fullstack",
    "JOB0309": "IT Project Analyst",
    "JOB0317": "Junior Software Engineer (Clearance Sponsorship)",
    "JOB0325": "Junior Software Integration Engineer",
    "JOB0332": "Junior AI Data Engineer",
    "JOB0336": "2026 Intern - Experience Design",
    "JOB0338": "Data Science Intern",
    "JOB0342": "Intern, Software Engineering",
    "JOB0351": "2026 Summer Internship - Backend Software Engineering Intern",
    "JOB0364": "Associate Software Development Engineering in Test Intern",
    "JOB0366": "Software Engineer Intern, Streaming Media",
    "JOB0393": "Software Engineering - Intern, Bachelor’s",
    "JOB0404": "Software Engineer - Intern (Summer 2026)",
    "JOB0446": "FOOD SERVICE WORKER (PART TIME)",
    "JOB0448": "Software Engineer - Intern (Summer 2026)",
    "JOB0450": "Software Developer Intern",
}


# --------------------------------------------------
# Load jobs
# --------------------------------------------------

jobs = pd.read_csv(JOBS_FILE)

print("=== MISSING JOB TITLE RECOVERY ===")
print()

print(f"Jobs loaded: {len(jobs)}")

print(
    f"Missing titles before recovery: "
    f"{jobs['job_title'].isna().sum()}"
)


# --------------------------------------------------
# Validate recovery mapping
# --------------------------------------------------

unknown_job_ids = (
    set(verified_titles.keys())
    - set(jobs["job_id"])
)

print()
print("--- MAPPING VALIDATION ---")

print(
    f"Verified title mappings: "
    f"{len(verified_titles)}"
)

print(
    f"Unknown job IDs: "
    f"{len(unknown_job_ids)}"
)

if unknown_job_ids:
    print(
        "Unknown IDs:",
        sorted(unknown_job_ids)
    )


# --------------------------------------------------
# Preserve original titles
# --------------------------------------------------

jobs["job_title_original"] = jobs["job_title"]

jobs["title_recovery_source"] = pd.NA


# --------------------------------------------------
# Recover missing titles
# --------------------------------------------------

for job_id, recovered_title in verified_titles.items():

    mask = (
        (jobs["job_id"] == job_id)
        & (jobs["job_title"].isna())
    )

    jobs.loc[
        mask,
        "job_title"
    ] = recovered_title

    jobs.loc[
        mask,
        "title_recovery_source"
    ] = "application_email"


# --------------------------------------------------
# Validate recovery results
# --------------------------------------------------

recovered_count = (
    jobs["title_recovery_source"]
    .eq("application_email")
    .sum()
)

print()
print("--- RECOVERY RESULTS ---")

print(
    f"Titles recovered: "
    f"{recovered_count}"
)

print(
    f"Titles present after recovery: "
    f"{jobs['job_title'].notna().sum()}"
)

print(
    f"Missing titles after recovery: "
    f"{jobs['job_title'].isna().sum()}"
)


# --------------------------------------------------
# Validate original titles were not changed
# --------------------------------------------------

originally_present = (
    jobs["job_title_original"].notna()
)

changed_original_titles = (
    jobs.loc[
        originally_present,
        "job_title"
    ]
    !=
    jobs.loc[
        originally_present,
        "job_title_original"
    ]
).sum()

print()
print("--- ORIGINAL DATA PRESERVATION ---")

print(
    f"Previously known titles changed: "
    f"{changed_original_titles}"
)


# --------------------------------------------------
# Build recovery audit
# --------------------------------------------------

recovery_audit = jobs[
    jobs["title_recovery_source"].notna()
][
    [
        "job_id",
        "company_name",
        "job_title_original",
        "job_title",
        "title_recovery_source"
    ]
].copy()

recovery_audit = recovery_audit.rename(
    columns={
        "job_title_original": "original_job_title",
        "job_title": "recovered_job_title",
        "title_recovery_source": "recovery_source"
    }
)


# --------------------------------------------------
# Build clean analytical jobs table
# --------------------------------------------------

analytical_jobs = jobs[
    [
        "job_id",
        "company_name",
        "job_title",
        "job_reference_id"
    ]
].copy()


# --------------------------------------------------
# Save outputs
# --------------------------------------------------

analytical_jobs.to_csv(
    JOBS_ENRICHED_FILE,
    index=False
)

recovery_audit.to_csv(
    RECOVERY_AUDIT_FILE,
    index=False
)

print()
print("=" * 70)
print("ENRICHED JOB OUTPUTS CREATED")
print("=" * 70)

print(
    f"Analytical jobs: "
    f"{len(analytical_jobs)}"
)

print(
    f"Recovery audit rows: "
    f"{len(recovery_audit)}"
)

print()

print(
    f"Jobs saved to: "
    f"{JOBS_ENRICHED_FILE}"
)

print(
    f"Audit saved to: "
    f"{RECOVERY_AUDIT_FILE}"
)


# --------------------------------------------------
# Post-save validation
# --------------------------------------------------

saved_jobs = pd.read_csv(
    JOBS_ENRICHED_FILE
)

saved_audit = pd.read_csv(
    RECOVERY_AUDIT_FILE
)

print()
print("=" * 70)
print("POST-SAVE VALIDATION")
print("=" * 70)

print()
print("--- JOBS ---")

print(
    f"Saved jobs: "
    f"{len(saved_jobs)}"
)

print(
    f"Unique job IDs: "
    f"{saved_jobs['job_id'].nunique()}"
)

print(
    f"Duplicate job IDs: "
    f"{saved_jobs['job_id'].duplicated().sum()}"
)

print(
    f"Missing job IDs: "
    f"{saved_jobs['job_id'].isna().sum()}"
)

print()
print("--- TITLES ---")

print(
    f"Titles present: "
    f"{saved_jobs['job_title'].notna().sum()}"
)

print(
    f"Titles missing: "
    f"{saved_jobs['job_title'].isna().sum()}"
)

print()
print("--- RECOVERY AUDIT ---")

print(
    f"Audit rows: "
    f"{len(saved_audit)}"
)

print(
    f"Unique recovered job IDs: "
    f"{saved_audit['job_id'].nunique()}"
)

print(
    f"Duplicate audit job IDs: "
    f"{saved_audit['job_id'].duplicated().sum()}"
)

print(
    f"Missing recovered titles: "
    f"{saved_audit['recovered_job_title'].isna().sum()}"
)

print()
print("--- ANALYTICAL JOB COLUMNS ---")

print(
    saved_jobs.columns.tolist()
)

print()
print("--- RECOVERED TITLE SAMPLE ---")

print(
    saved_audit[
        [
            "job_id",
            "company_name",
            "recovered_job_title",
            "recovery_source"
        ]
    ]
    .head(10)
    .to_string(index=False)
)