from pathlib import Path

import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

TITLE_AUDIT_FILE = Path(
    "data/processed/jobs_with_clean_titles.csv"
)

OUTPUT_FILE = Path(
    "data/processed/job_role_category_audit.csv"
)


# --------------------------------------------------
# Load title audit
# --------------------------------------------------

jobs = pd.read_csv(TITLE_AUDIT_FILE)

print("=== STAGE 4.2: JOB ROLE CATEGORY AUDIT ===")
print()

print(f"Jobs loaded: {len(jobs)}")


# --------------------------------------------------
# Role classification
# --------------------------------------------------

def classify_role(title):

    if pd.isna(title):
        return "Unknown"

    title = str(title).lower()


    # ----------------------------------------------
    # Business Intelligence
    # ----------------------------------------------

    if (
        "business intelligence" in title
        or "bi analyst" in title
        or "bi developer" in title
        or "power bi" in title
    ):
        return "Business Intelligence"


    # ----------------------------------------------
    # Data Science
    # ----------------------------------------------

    if (
        "data scientist" in title
        or "data science" in title
        or "biostatistician" in title
        or "research scientist" in title
        or "associate scientist, data" in title
    ):
        return "Data Science"


    # ----------------------------------------------
    # AI / Machine Learning
    # ----------------------------------------------

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


    # ----------------------------------------------
    # Data Engineering
    # ----------------------------------------------

    if (
        "data engineer" in title
        or "data engineering" in title
        or "etl engineer" in title
        or "aws/etl" in title
        or "data operations" in title
    ):
        return "Data Engineering"


    # ----------------------------------------------
    # Data / Analytics Analyst
    # ----------------------------------------------

    if (
        "data analyst" in title
        or "data analytics" in title
        or "analytics analyst" in title
        or "data & analytics" in title
        or "analyst, data" in title
    ):
        return "Data / Analytics Analyst"


    # ----------------------------------------------
    # Software Engineering / Development
    # ----------------------------------------------

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


    # ----------------------------------------------
    # QA / Testing
    # ----------------------------------------------

    if (
        "test engineer" in title
        or "qa engineer" in title
        or "qa tester" in title
        or "quality assurance" in title
        or "engineering in test" in title
        or "test automation" in title
    ):
        return "QA / Testing"


    # ----------------------------------------------
    # Information Technology
    # ----------------------------------------------

    if (
        "information technology" in title
        or "it support" in title
        or "it intern" in title
        or "it co-op" in title
        or "end user technologies" in title
    ):
        return "Information Technology"


    # ----------------------------------------------
    # General Analyst
    # ----------------------------------------------

    if "analyst" in title:
        return "Other Analyst"


    # ----------------------------------------------
    # General Engineering
    # ----------------------------------------------

    if "engineer" in title:
        return "Other Engineering"


    # ----------------------------------------------
    # General Developer
    # ----------------------------------------------

    if (
        "developer" in title
        or "programmer" in title
    ):
        return "Other Development"


    # ----------------------------------------------
    # Everything else
    # ----------------------------------------------

    return "Other"

# --------------------------------------------------
# Apply classification
# --------------------------------------------------

jobs["role_category"] = (
    jobs["job_title_clean"]
    .apply(classify_role)
)


# --------------------------------------------------
# Category distribution
# --------------------------------------------------

category_counts = (
    jobs["role_category"]
    .value_counts()
)


print()
print("--- ROLE CATEGORY DISTRIBUTION ---")

print(
    category_counts.to_string()
)


# --------------------------------------------------
# Category percentages
# --------------------------------------------------

category_percentages = (
    jobs["role_category"]
    .value_counts(normalize=True)
    .mul(100)
    .round(1)
)


print()
print("--- ROLE CATEGORY PERCENTAGES ---")

for category, percentage in category_percentages.items():

    print(
        f"{category}: {percentage}%"
    )


# --------------------------------------------------
# Inspect Other category
# --------------------------------------------------

other_jobs = jobs[
    jobs["role_category"] == "Other"
].copy()


print()
print("--- OTHER CATEGORY ---")

print(
    f"Jobs classified as Other: "
    f"{len(other_jobs)}"
)

print()

print(
    other_jobs[
        [
            "job_id",
            "company_name",
            "job_title",
            "job_title_clean"
        ]
    ]
    .head(50)
    .to_string(index=False)
)


# --------------------------------------------------
# Save audit
# --------------------------------------------------

jobs.to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print("--- OUTPUT ---")

print(
    f"Audit rows: "
    f"{len(jobs)}"
)

print(
    f"Saved to: "
    f"{OUTPUT_FILE}"
)