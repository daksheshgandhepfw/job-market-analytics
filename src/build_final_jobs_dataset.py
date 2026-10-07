from pathlib import Path

import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

JOBS_FILE = Path(
    "data/processed/jobs_with_clean_titles.csv"
)

OUTPUT_FILE = Path(
    "data/processed/jobs_final.csv"
)


# --------------------------------------------------
# Load jobs
# --------------------------------------------------

jobs = pd.read_csv(JOBS_FILE)


print("=== BUILD FINAL ANALYTICAL JOBS DATASET ===")
print()

print(f"Jobs loaded: {len(jobs)}")


# --------------------------------------------------
# Role-category classification
# --------------------------------------------------

def classify_role(title):

    if pd.isna(title):
        return "Unknown"

    title = str(title).lower()

    # Business Intelligence
    if (
        "business intelligence" in title
        or "bi analyst" in title
        or "bi developer" in title
        or "power bi" in title
    ):
        return "Business Intelligence"

    # Data Science
    if (
        "data scientist" in title
        or "data science" in title
        or "biostatistician" in title
        or "research scientist" in title
        or "associate scientist, data" in title
    ):
        return "Data Science"

    # AI / Machine Learning
    if (
        "machine learning" in title
        or "ml engineer" in title
        or "ai engineer" in title
        or "ai programmer" in title
        or "artificial intelligence" in title
        or "ai & analytics" in title
        or "ai/data analytics" in title
    ):
        return "AI / Machine Learning"

    # Data Engineering
    if (
        "data engineer" in title
        or "data engineering" in title
        or "etl engineer" in title
        or "aws/etl" in title
        or "data operations" in title
    ):
        return "Data Engineering"

    # Data / Analytics Analyst
    if (
        "data analyst" in title
        or "data analytics" in title
        or "analytics analyst" in title
        or "data & analytics" in title
        or "analyst, data" in title
    ):
        return "Data / Analytics Analyst"

    # Software Engineering
    if (
        "software engineer" in title
        or "software engineering" in title
        or "software developer" in title
        or "software development" in title
        or "full-stack" in title
        or "full stack" in title
        or "backend engineer" in title
        or "backend software" in title
        or "web design/ development" in title
        or "web design/development" in title
    ):
        return "Software Engineering"

    # QA / Testing
    if (
        "test engineer" in title
        or "qa engineer" in title
        or "qa tester" in title
        or "quality assurance" in title
        or "engineering in test" in title
        or "test automation" in title
    ):
        return "QA / Testing"

    # Information Technology
    if (
        "information technology" in title
        or "it support" in title
        or "it intern" in title
        or "it co-op" in title
        or "end user technologies" in title
    ):
        return "Information Technology"

    # General Analyst
    if "analyst" in title:
        return "Other Analyst"

    # General Engineering
    if "engineer" in title:
        return "Other Engineering"

    # General Development
    if (
        "developer" in title
        or "programmer" in title
    ):
        return "Other Development"

    return "Other"


# --------------------------------------------------
# Career-level classification
# --------------------------------------------------

def classify_career_level(title):

    if pd.isna(title):
        return "Unknown"

    title = str(title).lower()

    # Internship / Co-op
    if (
        "intern" in title
        or "internship" in title
        or "co-op" in title
        or "coop" in title
    ):
        return "Internship / Co-op"

    # New Graduate / Early Career
    if (
        "new grad" in title
        or "new graduate" in title
        or "campus graduate" in title
        or "graduate program" in title
        or "graduate development program" in title
        or "early career" in title
    ):
        return "New Graduate / Early Career"

    # Entry Level / Junior
    if (
        "entry level" in title
        or "entry-level" in title
        or "junior" in title
        or " jr " in f" {title} "
        or title.endswith(" jr")
        or ", jr" in title
    ):
        return "Entry Level / Junior"

    # Associate
    if "associate" in title:
        return "Associate"

    # Senior
    if (
        "senior" in title
        or " sr " in f" {title} "
        or title.endswith(" sr")
        or ", sr" in title
    ):
        return "Senior"

    # Management
    if (
        "manager" in title
        or "director" in title
        or "vice president" in title
        or "vp " in title
        or title.startswith("vp ")
    ):
        return "Management"

    # Lead / Principal / Staff
    if (
        "lead" in title
        or "principal" in title
        or "staff engineer" in title
        or "staff data" in title
        or "staff software" in title
    ):
        return "Lead / Principal / Staff"

    return "Unspecified"


# --------------------------------------------------
# Apply classifications
# --------------------------------------------------

jobs["role_category"] = (
    jobs["job_title_clean"]
    .apply(classify_role)
)

jobs["career_level"] = (
    jobs["job_title_clean"]
    .apply(classify_career_level)
)


# --------------------------------------------------
# Build final analytical table
# --------------------------------------------------

final_jobs = jobs[
    [
        "job_id",
        "company_name",
        "job_title",
        "job_title_clean",
        "role_category",
        "career_level",
        "job_reference_id"
    ]
].copy()


# --------------------------------------------------
# Pre-save validation
# --------------------------------------------------

print()
print("--- PRE-SAVE VALIDATION ---")

print(
    f"Final jobs: "
    f"{len(final_jobs)}"
)

print(
    f"Unique job IDs: "
    f"{final_jobs['job_id'].nunique()}"
)

print(
    f"Duplicate job IDs: "
    f"{final_jobs['job_id'].duplicated().sum()}"
)

print(
    f"Missing job IDs: "
    f"{final_jobs['job_id'].isna().sum()}"
)

print(
    f"Clean titles present: "
    f"{final_jobs['job_title_clean'].notna().sum()}"
)

print(
    f"Clean titles missing: "
    f"{final_jobs['job_title_clean'].isna().sum()}"
)


# --------------------------------------------------
# Role-category validation
# --------------------------------------------------

print()
print("--- ROLE CATEGORY DISTRIBUTION ---")

print(
    final_jobs["role_category"]
    .value_counts()
    .to_string()
)


# --------------------------------------------------
# Career-level validation
# --------------------------------------------------

print()
print("--- CAREER LEVEL DISTRIBUTION ---")

print(
    final_jobs["career_level"]
    .value_counts()
    .to_string()
)


# --------------------------------------------------
# Save
# --------------------------------------------------

final_jobs.to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print("=" * 70)
print("FINAL JOBS DATASET CREATED")
print("=" * 70)

print(
    f"Saved to: "
    f"{OUTPUT_FILE}"
)


# --------------------------------------------------
# Post-save validation
# --------------------------------------------------

saved_jobs = pd.read_csv(
    OUTPUT_FILE
)


print()
print("--- POST-SAVE VALIDATION ---")

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


expected_columns = [
    "job_id",
    "company_name",
    "job_title",
    "job_title_clean",
    "role_category",
    "career_level",
    "job_reference_id"
]


print()
print("--- SCHEMA VALIDATION ---")

print(
    f"Columns correct: "
    f"{saved_jobs.columns.tolist() == expected_columns}"
)

print(
    saved_jobs.columns.tolist()
)


print()
print("--- REQUIRED ANALYTICAL FIELDS ---")

print(
    f"Missing role categories: "
    f"{saved_jobs['role_category'].isna().sum()}"
)

print(
    f"Missing career levels: "
    f"{saved_jobs['career_level'].isna().sum()}"
)

print(
    f"Unknown role categories: "
    f"{saved_jobs['role_category'].eq('Unknown').sum()}"
)

print(
    f"Unknown career levels: "
    f"{saved_jobs['career_level'].eq('Unknown').sum()}"
)


print()
print("--- SAMPLE ---")

print(
    saved_jobs.head(10)
    .to_string(index=False)
)