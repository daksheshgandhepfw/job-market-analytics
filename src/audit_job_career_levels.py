from pathlib import Path

import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

JOBS_FILE = Path(
    "data/processed/jobs_with_clean_titles.csv"
)

OUTPUT_FILE = Path(
    "data/processed/job_career_level_audit.csv"
)


# --------------------------------------------------
# Load jobs
# --------------------------------------------------

jobs = pd.read_csv(JOBS_FILE)


print("=== STAGE 4.6: CAREER LEVEL CLASSIFICATION AUDIT ===")
print()

print(
    f"Jobs loaded: "
    f"{len(jobs)}"
)

print(
    f"Jobs with clean title: "
    f"{jobs['job_title_clean'].notna().sum()}"
)

print(
    f"Jobs without clean title: "
    f"{jobs['job_title_clean'].isna().sum()}"
)


# --------------------------------------------------
# Career-level classification
# --------------------------------------------------

def classify_career_level(title):

    if pd.isna(title):
        return "Unknown"

    title = str(title).lower()


    # ----------------------------------------------
    # Internship / Co-op
    # ----------------------------------------------

    if (
        "intern" in title
        or "internship" in title
        or "co-op" in title
        or "coop" in title
    ):
        return "Internship / Co-op"


    # ----------------------------------------------
    # New Graduate
    # ----------------------------------------------

    if (
        "new grad" in title
        or "new graduate" in title
        or "campus graduate" in title
        or "graduate program" in title
        or "graduate development program" in title
        or "early career" in title
    ):
        return "New Graduate / Early Career"


    # ----------------------------------------------
    # Entry Level / Junior
    # ----------------------------------------------

    if (
        "entry level" in title
        or "entry-level" in title
        or "junior" in title
        or " jr " in f" {title} "
        or title.endswith(" jr")
        or ", jr" in title
    ):
        return "Entry Level / Junior"


    # ----------------------------------------------
    # Associate
    # ----------------------------------------------

    if "associate" in title:
        return "Associate"


    # ----------------------------------------------
    # Senior
    # ----------------------------------------------

    if (
        "senior" in title
        or " sr " in f" {title} "
        or title.endswith(" sr")
        or ", sr" in title
    ):
        return "Senior"


    # ----------------------------------------------
    # Management
    # ----------------------------------------------

    if (
        "manager" in title
        or "director" in title
        or "vice president" in title
        or "vp " in title
        or title.startswith("vp ")
    ):
        return "Management"


    # ----------------------------------------------
    # Lead / Principal / Staff
    # ----------------------------------------------

    if (
        "lead" in title
        or "principal" in title
        or "staff engineer" in title
        or "staff data" in title
        or "staff software" in title
    ):
        return "Lead / Principal / Staff"


    # ----------------------------------------------
    # No explicit level
    # ----------------------------------------------

    return "Unspecified"


# --------------------------------------------------
# Apply classification
# --------------------------------------------------

jobs["career_level"] = (
    jobs["job_title_clean"]
    .apply(classify_career_level)
)


# --------------------------------------------------
# Distribution
# --------------------------------------------------

level_counts = (
    jobs["career_level"]
    .value_counts()
)


print()
print("--- CAREER LEVEL DISTRIBUTION ---")

print(
    level_counts.to_string()
)


# --------------------------------------------------
# Percentages
# --------------------------------------------------

level_percentages = (
    jobs["career_level"]
    .value_counts(normalize=True)
    .mul(100)
    .round(1)
)


print()
print("--- CAREER LEVEL PERCENTAGES ---")

for level, percentage in level_percentages.items():

    print(
        f"{level}: {percentage}%"
    )


# --------------------------------------------------
# Inspect classified early-career jobs
# --------------------------------------------------

early_career_levels = [
    "Internship / Co-op",
    "New Graduate / Early Career",
    "Entry Level / Junior",
    "Associate"
]


early_career_jobs = jobs[
    jobs["career_level"].isin(
        early_career_levels
    )
].copy()


print()
print("--- EARLY-CAREER JOBS ---")

print(
    f"Early-career classified jobs: "
    f"{len(early_career_jobs)}"
)

print()

print(
    early_career_jobs[
        [
            "job_id",
            "company_name",
            "job_title_clean",
            "career_level"
        ]
    ]
    .head(50)
    .to_string(index=False)
)


# --------------------------------------------------
# Inspect senior / management classifications
# --------------------------------------------------

higher_level_jobs = jobs[
    jobs["career_level"].isin(
        [
            "Senior",
            "Management",
            "Lead / Principal / Staff"
        ]
    )
].copy()


print()
print("--- HIGHER-LEVEL JOBS ---")

print(
    f"Higher-level classified jobs: "
    f"{len(higher_level_jobs)}"
)

if len(higher_level_jobs) > 0:

    print()

    print(
        higher_level_jobs[
            [
                "job_id",
                "company_name",
                "job_title_clean",
                "career_level"
            ]
        ]
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