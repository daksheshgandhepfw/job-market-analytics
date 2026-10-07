from pathlib import Path

import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

JOBS_FILE = Path(
    "data/processed/jobs_enriched.csv"
)

OUTPUT_FILE = Path(
    "data/processed/suspicious_job_title_audit.csv"
)


# --------------------------------------------------
# Load jobs
# --------------------------------------------------

jobs = pd.read_csv(JOBS_FILE)

jobs_with_titles = jobs[
    jobs["job_title"].notna()
].copy()


print("=== STAGE 4.3: SUSPICIOUS JOB TITLE AUDIT ===")
print()

print(
    f"Jobs with titles: "
    f"{len(jobs_with_titles)}"
)


# --------------------------------------------------
# Normalize titles
# --------------------------------------------------

jobs_with_titles["job_title_normalized"] = (
    jobs_with_titles["job_title"]
    .astype(str)
    .str.strip()
    .str.lower()
    .str.replace(
        r"\s+",
        " ",
        regex=True
    )
)


# --------------------------------------------------
# Suspicious phrase rules
# --------------------------------------------------

suspicious_patterns = {

    "generic_position":
        r"^(a |the )?position\b",

    "generic_opportunity":
        r"^(an |the )?opportunity\b",

    "generic_role":
        r"^(a |the )?role\b",

    "generic_employment":
        r"^employment\b",

    "generic_team":
        r"^our team\b",

    "generic_potential":
        r"^potential opportunities\b",

    "sentence_fragment":
        r"^(and |we |your |thank |thanks )",

    "position_suffix":
        r"\bposition at\b|\bposition with\b",

    "prose_suffix":
        r"\bopportunity at\b|\bopportunity with\b",
}


# --------------------------------------------------
# Detect suspicious titles
# --------------------------------------------------

def detect_suspicious_reason(title):

    for reason, pattern in suspicious_patterns.items():

        if pd.Series([title]).str.contains(
            pattern,
            regex=True,
            case=False,
            na=False
        ).iloc[0]:

            return reason

    return None


jobs_with_titles["suspicious_reason"] = (
    jobs_with_titles["job_title_normalized"]
    .apply(detect_suspicious_reason)
)


# --------------------------------------------------
# Build suspicious title audit
# --------------------------------------------------

suspicious_jobs = jobs_with_titles[
    jobs_with_titles["suspicious_reason"].notna()
].copy()


print()
print("--- SUSPICIOUS TITLE RESULTS ---")

print(
    f"Suspicious titles: "
    f"{len(suspicious_jobs)}"
)

print(
    f"Unique jobs: "
    f"{suspicious_jobs['job_id'].nunique()}"
)


# --------------------------------------------------
# Reason distribution
# --------------------------------------------------

print()
print("--- SUSPICIOUS REASON DISTRIBUTION ---")

print(
    suspicious_jobs[
        "suspicious_reason"
    ]
    .value_counts()
    .to_string()
)


# --------------------------------------------------
# Display suspicious titles
# --------------------------------------------------

print()
print("--- SUSPICIOUS TITLES ---")

if len(suspicious_jobs) == 0:

    print("No suspicious titles detected.")

else:

    print(
        suspicious_jobs[
            [
                "job_id",
                "company_name",
                "job_title",
                "suspicious_reason"
            ]
        ]
        .sort_values(
            [
                "suspicious_reason",
                "job_id"
            ]
        )
        .to_string(index=False)
    )


# --------------------------------------------------
# Save audit
# --------------------------------------------------

suspicious_jobs[
    [
        "job_id",
        "company_name",
        "job_title",
        "suspicious_reason"
    ]
].to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print("--- OUTPUT ---")

print(
    f"Audit rows: "
    f"{len(suspicious_jobs)}"
)

print(
    f"Saved to: "
    f"{OUTPUT_FILE}"
)