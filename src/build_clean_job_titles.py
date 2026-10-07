from pathlib import Path

import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

JOBS_FILE = Path(
    "data/processed/jobs_enriched.csv"
)

OUTPUT_FILE = Path(
    "data/processed/jobs_with_clean_titles.csv"
)

CLEANING_AUDIT_FILE = Path(
    "data/processed/job_title_cleaning_audit.csv"
)


# --------------------------------------------------
# Manually verified analytical title corrections
# --------------------------------------------------

title_corrections = {
    "JOB0061": "Data Engineering Co-op",
    "JOB0064": "Data Engineering Co-op",
    "JOB0088": "Data Analyst Student",
    "JOB0100": "Machine Learning & Data Engineer",
    "JOB0140": "Software Engineer I",
    "JOB0170": "Associate Scientist, Data I",
    "JOB0207": "Analyst, Data Systems",
    "JOB0240": "Analyst",
    "JOB0271": "GIS Analyst",
    "JOB0283": "AI & Analytics Associate",
    "JOB0302": "Operational Data Scientist",
    "JOB0304": "Data Engineer",
    "JOB0334": "GIS (Geographic Information System) Intern",
    "JOB0341": "SW Engineer Support Intern",
    "JOB0376": "Software Engineer Intern, Settlement",
    "JOB0377": "IT Intern",
    "JOB0386": "Software Engineer Intern",
    "JOB0387": "AI/Data Analytics Intern",
    "JOB0395": "IT Support Intern",
    "JOB0399": "IT Intern",
    "JOB0402": "Sound Quality Benchmarking, Experiential R&D Intern",
    "JOB0424": "Project Management Intern",
    "JOB0432": "Software Developer Intern",
    "JOB0434": "Software Engineer - Test Equipment Intern",
}


# --------------------------------------------------
# Titles determined to be unusable
# --------------------------------------------------

unusable_titles = {
    "JOB0053",
    "JOB0079",
    "JOB0193",
    "JOB0204",
    "JOB0369",
    "JOB0378",
}


# --------------------------------------------------
# Load jobs
# --------------------------------------------------

jobs = pd.read_csv(JOBS_FILE)


print("=== STAGE 4.4: BUILD CLEAN JOB TITLES ===")
print()

print(
    f"Jobs loaded: "
    f"{len(jobs)}"
)

print(
    f"Original titles present: "
    f"{jobs['job_title'].notna().sum()}"
)

print(
    f"Original titles missing: "
    f"{jobs['job_title'].isna().sum()}"
)


# --------------------------------------------------
# Validate manual job IDs
# --------------------------------------------------

manual_job_ids = (
    set(title_corrections.keys())
    | unusable_titles
)

unknown_job_ids = (
    manual_job_ids
    - set(jobs["job_id"])
)


print()
print("--- MANUAL RULE VALIDATION ---")

print(
    f"Title corrections: "
    f"{len(title_corrections)}"
)

print(
    f"Unusable titles: "
    f"{len(unusable_titles)}"
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
# Create clean analytical title
# --------------------------------------------------

jobs["job_title_clean"] = jobs["job_title"]

jobs["title_cleaning_action"] = "unchanged"


# --------------------------------------------------
# Apply verified corrections
# --------------------------------------------------

for job_id, clean_title in title_corrections.items():

    mask = (
        jobs["job_id"] == job_id
    )

    jobs.loc[
        mask,
        "job_title_clean"
    ] = clean_title

    jobs.loc[
        mask,
        "title_cleaning_action"
    ] = "cleaned"


# --------------------------------------------------
# Remove unusable extracted titles
# --------------------------------------------------

for job_id in unusable_titles:

    mask = (
        jobs["job_id"] == job_id
    )

    jobs.loc[
        mask,
        "job_title_clean"
    ] = pd.NA

    jobs.loc[
        mask,
        "title_cleaning_action"
    ] = "set_missing"


# --------------------------------------------------
# Mark originally missing titles
# --------------------------------------------------

originally_missing = (
    jobs["job_title"].isna()
)

jobs.loc[
    originally_missing,
    "title_cleaning_action"
] = "originally_missing"


# --------------------------------------------------
# Validation
# --------------------------------------------------

print()
print("--- CLEANING RESULTS ---")

print(
    jobs["title_cleaning_action"]
    .value_counts()
    .to_string()
)

print()

print(
    f"Clean titles present: "
    f"{jobs['job_title_clean'].notna().sum()}"
)

print(
    f"Clean titles missing: "
    f"{jobs['job_title_clean'].isna().sum()}"
)


# --------------------------------------------------
# Build cleaning audit
# --------------------------------------------------

cleaning_audit = jobs[
    jobs["title_cleaning_action"].isin(
        [
            "cleaned",
            "set_missing"
        ]
    )
][
    [
        "job_id",
        "company_name",
        "job_title",
        "job_title_clean",
        "title_cleaning_action"
    ]
].copy()


# --------------------------------------------------
# Build analytical output
# --------------------------------------------------

analytical_jobs = jobs[
    [
        "job_id",
        "company_name",
        "job_title",
        "job_title_clean",
        "job_reference_id"
    ]
].copy()


# --------------------------------------------------
# Save outputs
# --------------------------------------------------

analytical_jobs.to_csv(
    OUTPUT_FILE,
    index=False
)

cleaning_audit.to_csv(
    CLEANING_AUDIT_FILE,
    index=False
)


print()
print("=" * 70)
print("CLEAN JOB TITLE OUTPUTS CREATED")
print("=" * 70)

print(
    f"Analytical jobs: "
    f"{len(analytical_jobs)}"
)

print(
    f"Cleaning audit rows: "
    f"{len(cleaning_audit)}"
)

print()

print(
    f"Jobs saved to: "
    f"{OUTPUT_FILE}"
)

print(
    f"Audit saved to: "
    f"{CLEANING_AUDIT_FILE}"
)


# --------------------------------------------------
# Post-save validation
# --------------------------------------------------

saved_jobs = pd.read_csv(
    OUTPUT_FILE
)

saved_audit = pd.read_csv(
    CLEANING_AUDIT_FILE
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
print("--- CLEAN TITLES ---")

print(
    f"Clean titles present: "
    f"{saved_jobs['job_title_clean'].notna().sum()}"
)

print(
    f"Clean titles missing: "
    f"{saved_jobs['job_title_clean'].isna().sum()}"
)


print()
print("--- CLEANING AUDIT ---")

print(
    f"Audit rows: "
    f"{len(saved_audit)}"
)

print(
    f"Cleaned rows: "
    f"{saved_audit['title_cleaning_action'].eq('cleaned').sum()}"
)

print(
    f"Set-missing rows: "
    f"{saved_audit['title_cleaning_action'].eq('set_missing').sum()}"
)

print(
    f"Unique audit job IDs: "
    f"{saved_audit['job_id'].nunique()}"
)


print()
print("--- CLEANING SAMPLE ---")

print(
    saved_audit[
        [
            "job_id",
            "job_title",
            "job_title_clean",
            "title_cleaning_action"
        ]
    ]
    .head(15)
    .to_string(index=False)
)