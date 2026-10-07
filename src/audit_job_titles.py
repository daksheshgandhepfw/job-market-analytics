from pathlib import Path

import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

JOBS_FILE = Path(
    "data/processed/jobs_enriched.csv"
)


# --------------------------------------------------
# Load jobs
# --------------------------------------------------

jobs = pd.read_csv(JOBS_FILE)


print("=== STAGE 4.1: JOB TITLE AUDIT ===")
print()

print(f"Total jobs: {len(jobs)}")

print(
    f"Jobs with title: "
    f"{jobs['job_title'].notna().sum()}"
)

print(
    f"Jobs without title: "
    f"{jobs['job_title'].isna().sum()}"
)


# --------------------------------------------------
# Normalize titles for audit
# --------------------------------------------------

def normalize_title(value):

    if pd.isna(value):
        return None

    value = str(value).strip().lower()

    if value == "":
        return None

    return " ".join(value.split())


jobs["job_title_normalized"] = (
    jobs["job_title"]
    .apply(normalize_title)
)


# --------------------------------------------------
# Title uniqueness
# --------------------------------------------------

titles = jobs[
    jobs["job_title_normalized"].notna()
].copy()


print()
print("--- TITLE UNIQUENESS ---")

print(
    f"Jobs with usable title: "
    f"{len(titles)}"
)

print(
    f"Unique normalized titles: "
    f"{titles['job_title_normalized'].nunique()}"
)


# --------------------------------------------------
# Most common titles
# --------------------------------------------------

title_counts = (
    titles["job_title_normalized"]
    .value_counts()
)


print()
print("--- MOST COMMON TITLES ---")

print(
    title_counts
    .head(30)
    .to_string()
)


# --------------------------------------------------
# Keyword coverage
# --------------------------------------------------

keywords = {
    "data": r"\bdata\b",
    "analyst": r"\banalyst\b",
    "analytics": r"\banalytics\b",
    "engineer": r"\bengineer\b",
    "engineering": r"\bengineering\b",
    "software": r"\bsoftware\b",
    "developer": r"\bdeveloper\b",
    "scientist": r"\bscientist\b",
    "science": r"\bscience\b",
    "machine learning": r"\bmachine learning\b",
    "ml": r"\bml\b",
    "artificial intelligence": r"\bartificial intelligence\b",
    "ai": r"\bai\b",
    "business intelligence": r"\bbusiness intelligence\b",
    "bi": r"\bbi\b",
    "intern": r"\bintern(ship)?\b",
}


print()
print("--- KEYWORD COVERAGE ---")

for label, pattern in keywords.items():

    count = (
        titles["job_title_normalized"]
        .str.contains(
            pattern,
            regex=True,
            na=False
        )
        .sum()
    )

    print(
        f"{label}: {count}"
    )


# --------------------------------------------------
# Seniority / early-career language
# --------------------------------------------------

seniority_patterns = {
    "intern": r"\bintern(ship)?\b",
    "junior": r"\bjunior\b|\bjr\b",
    "entry level": r"\bentry[\s-]?level\b",
    "associate": r"\bassociate\b",
    "new grad": r"\bnew[\s-]?grad\b|\bgraduate\b",
    "senior": r"\bsenior\b|\bsr\b",
    "lead": r"\blead\b",
    "manager": r"\bmanager\b",
    "director": r"\bdirector\b",
}


print()
print("--- SENIORITY LANGUAGE ---")

for label, pattern in seniority_patterns.items():

    count = (
        titles["job_title_normalized"]
        .str.contains(
            pattern,
            regex=True,
            na=False
        )
        .sum()
    )

    print(
        f"{label}: {count}"
    )


# --------------------------------------------------
# Save title audit for inspection
# --------------------------------------------------

TITLE_AUDIT_FILE = Path(
    "data/processed/job_title_audit.csv"
)

title_audit = (
    titles[
        [
            "job_id",
            "company_name",
            "job_title",
            "job_title_normalized"
        ]
    ]
    .sort_values(
        "job_title_normalized"
    )
)

title_audit.to_csv(
    TITLE_AUDIT_FILE,
    index=False
)


print()
print("--- OUTPUT ---")

print(
    f"Title audit rows: "
    f"{len(title_audit)}"
)

print(
    f"Saved to: "
    f"{TITLE_AUDIT_FILE}"
)