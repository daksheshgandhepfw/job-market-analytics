import pandas as pd
from pathlib import Path


# --------------------------------------------------
# File paths
# --------------------------------------------------

JOBS_FILE = Path("data/processed/jobs.csv")
APPLICATIONS_FILE = Path("data/processed/applications.csv")
EMAILS_FILE = Path("data/processed/final_enriched_job_emails.csv")


# --------------------------------------------------
# Load datasets
# --------------------------------------------------

jobs = pd.read_csv(JOBS_FILE)
applications = pd.read_csv(APPLICATIONS_FILE)
emails = pd.read_csv(EMAILS_FILE)


print("=== STAGE 3.4: MISSING JOB TITLE RECOVERY AUDIT ===")
print()

print(f"Jobs loaded: {len(jobs)}")
print(f"Applications loaded: {len(applications)}")
print(f"Emails loaded: {len(emails)}")


# --------------------------------------------------
# Identify jobs with missing titles
# --------------------------------------------------

missing_title_jobs = jobs[
    jobs["job_title"].isna()
].copy()

print()
print("--- MISSING TITLE JOBS ---")
print(f"Jobs missing title: {len(missing_title_jobs)}")


# --------------------------------------------------
# Find applications belonging to those jobs
# --------------------------------------------------

missing_title_applications = applications[
    applications["job_id"].isin(
        missing_title_jobs["job_id"]
    )
].copy()

print()
print("--- LINKED APPLICATIONS ---")
print(
    f"Applications linked to missing-title jobs: "
    f"{len(missing_title_applications)}"
)


# --------------------------------------------------
# Expand email_ids into one row per email
# --------------------------------------------------

application_email_links = (
    missing_title_applications[
        ["application_id", "job_id", "email_ids"]
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
# Join source email information
# --------------------------------------------------

title_recovery_audit = (
    application_email_links
    .merge(
        emails[
            [
                "email_id",
                "email_type",
                "company_name",
                "subject",
                "email_body"
            ]
        ],
        on="email_id",
        how="left"
    )
)


# --------------------------------------------------
# Audit relationship
# --------------------------------------------------

print()
print("--- EMAIL LINKAGE ---")

print(
    f"Email links created: "
    f"{len(application_email_links)}"
)

print(
    f"Email links matched to source emails: "
    f"{title_recovery_audit['email_type'].notna().sum()}"
)

print(
    f"Email links unmatched: "
    f"{title_recovery_audit['email_type'].isna().sum()}"
)

print()
print(
    f"Missing-title jobs represented: "
    f"{title_recovery_audit['job_id'].nunique()}"
)

print(
    f"Missing-title applications represented: "
    f"{title_recovery_audit['application_id'].nunique()}"
)

# --------------------------------------------------
# Inspect subjects for missing-title jobs
# --------------------------------------------------

print()
print("=" * 70)
print("MISSING TITLE SUBJECT SAMPLE")
print("=" * 70)

subject_sample = (
    title_recovery_audit[
        [
            "job_id",
            "application_id",
            "company_name",
            "email_type",
            "subject"
        ]
    ]
    .drop_duplicates()
    .head(30)
)

print(
    subject_sample.to_string(
        index=False
    )
)

# --------------------------------------------------
# Create missing-title manual review file
# --------------------------------------------------

REVIEW_OUTPUT_FILE = Path(
    "data/processed/missing_job_title_review.csv"
)

title_review = (
    title_recovery_audit[
        [
            "job_id",
            "application_id",
            "email_id",
            "company_name",
            "email_type",
            "subject",
            "email_body"
        ]
    ]
    .copy()
)

# Columns that will later hold our review decisions
title_review["candidate_job_title"] = ""
title_review["title_found"] = ""
title_review["review_notes"] = ""

title_review.to_csv(
    REVIEW_OUTPUT_FILE,
    index=False
)

print()
print("=" * 70)
print("TITLE REVIEW FILE CREATED")
print("=" * 70)

print(f"Rows: {len(title_review)}")
print(
    f"Unique jobs: "
    f"{title_review['job_id'].nunique()}"
)
print(
    f"Unique applications: "
    f"{title_review['application_id'].nunique()}"
)

print()
print(f"Saved to: {REVIEW_OUTPUT_FILE}")

# --------------------------------------------------
# Audit common job-title phrases in email bodies
# --------------------------------------------------

print()
print("=" * 70)
print("JOB TITLE PHRASE AUDIT")
print("=" * 70)

phrase_patterns = {
    "applying for": r"\bapplying for\b",
    "applied for": r"\bapplied for\b",
    "application for": r"\bapplication for\b",
    "interest in": r"\binterest in\b",
    "received your application for": r"\breceived your application for\b",
    "position": r"\bposition\b",
    "role": r"\brole\b",
    "opportunity": r"\bopportunity\b",
}

email_bodies = (
    title_recovery_audit["email_body"]
    .fillna("")
    .astype(str)
)

print()

for phrase, pattern in phrase_patterns.items():

    count = (
        email_bodies
        .str.contains(
            pattern,
            case=False,
            regex=True
        )
        .sum()
    )

    print(f"{phrase}: {count}")

    # --------------------------------------------------
# Test candidate job-title extraction
# --------------------------------------------------

import re


def extract_candidate_title(body):

    if pd.isna(body):
        return None, None

    text = " ".join(str(body).split())

    patterns = [

        (
            "applying_for_position",
            r"(?:applying|applied)\s+for\s+(?:the\s+)?(.{2,120}?)\s+position\b"
        ),

        (
            "application_for_position",
            r"application\s+for\s+(?:the\s+)?(.{2,120}?)\s+position\b"
        ),

        (
            "received_application_for",
            r"received\s+your\s+application\s+for\s+(?:the\s+)?(.{2,120}?)(?:\s+position\b|[.!])"
        ),

        (
            "interest_in_position",
            r"interest\s+(?:you(?:'ve| have)\s+shown\s+)?in\s+(?:the\s+)?(.{2,120}?)\s+position\b"
        ),

        (
            "applying_for_role",
            r"(?:applying|applied)\s+for\s+(?:the\s+)?(.{2,120}?)\s+role\b"
        ),

        (
            "application_for_role",
            r"application\s+for\s+(?:the\s+)?(.{2,120}?)\s+role\b"
        ),
    ]

    for rule_name, pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            candidate = match.group(1).strip(
                " -–—:,.\"'"
            )

            return candidate, rule_name

    return None, None


candidate_results = (
    title_recovery_audit["email_body"]
    .apply(extract_candidate_title)
)

title_recovery_audit["candidate_job_title"] = (
    candidate_results.apply(lambda x: x[0])
)

title_recovery_audit["extraction_rule"] = (
    candidate_results.apply(lambda x: x[1])
)


print()
print("=" * 70)
print("CANDIDATE TITLE EXTRACTION")
print("=" * 70)

print(
    f"Email records: "
    f"{len(title_recovery_audit)}"
)

print(
    f"Candidates extracted: "
    f"{title_recovery_audit['candidate_job_title'].notna().sum()}"
)

print(
    f"No candidate extracted: "
    f"{title_recovery_audit['candidate_job_title'].isna().sum()}"
)

print(
    f"Jobs with at least one candidate: "
    f"{title_recovery_audit.loc[
        title_recovery_audit['candidate_job_title'].notna(),
        'job_id'
    ].nunique()}"
)

print()
print("--- EXTRACTION RULE COUNTS ---")

print(
    title_recovery_audit["extraction_rule"]
    .value_counts(dropna=False)
    .to_string()
)

# --------------------------------------------------
# Inspect extracted title candidates
# --------------------------------------------------

print()
print("=" * 70)
print("EXTRACTED TITLE CANDIDATES")
print("=" * 70)

candidate_review = (
    title_recovery_audit[
        title_recovery_audit["candidate_job_title"].notna()
    ][
        [
            "job_id",
            "application_id",
            "company_name",
            "candidate_job_title",
            "extraction_rule",
            "subject"
        ]
    ]
    .copy()
)

print(
    candidate_review.to_string(
        index=False
    )
)

# --------------------------------------------------
# Inspect beginning of missing-title email bodies
# --------------------------------------------------

print()
print("=" * 70)
print("MISSING TITLE EMAIL BODY PREVIEWS")
print("=" * 70)

preview_df = (
    title_recovery_audit[
        [
            "job_id",
            "company_name",
            "email_body"
        ]
    ]
    .drop_duplicates(subset=["job_id"])
    .copy()
)

preview_df["body_preview"] = (
    preview_df["email_body"]
    .fillna("")
    .astype(str)
    .str.replace(r"\s+", " ", regex=True)
    .str.slice(0, 300)
)

print(
    preview_df[
        [
            "job_id",
            "company_name",
            "body_preview"
        ]
    ]
    .head(30)
    .to_string(index=False)
)

# --------------------------------------------------
# Create compact title recovery review dataset
# --------------------------------------------------

COMPACT_REVIEW_FILE = Path(
    "data/processed/missing_job_title_compact_review.csv"
)

compact_review = (
    title_recovery_audit[
        [
            "job_id",
            "application_id",
            "company_name",
            "email_id",
            "email_type",
            "subject",
            "email_body"
        ]
    ]
    .drop_duplicates(subset=["job_id"])
    .copy()
)

compact_review["body_preview"] = (
    compact_review["email_body"]
    .fillna("")
    .astype(str)
    .str.replace(r"\s+", " ", regex=True)
    .str.slice(0, 500)
)

compact_review["recovered_job_title"] = ""
compact_review["recovery_status"] = ""
compact_review["recovery_notes"] = ""

compact_review = compact_review[
    [
        "job_id",
        "application_id",
        "company_name",
        "email_id",
        "email_type",
        "subject",
        "body_preview",
        "recovered_job_title",
        "recovery_status",
        "recovery_notes"
    ]
]

compact_review.to_csv(
    COMPACT_REVIEW_FILE,
    index=False
)

print()
print("=" * 70)
print("COMPACT TITLE REVIEW CREATED")
print("=" * 70)

print(f"Rows: {len(compact_review)}")
print(f"Unique jobs: {compact_review['job_id'].nunique()}")
print()
print(f"Saved to: {COMPACT_REVIEW_FILE}")

# --------------------------------------------------
# Flag strong title evidence
# --------------------------------------------------

def detect_title_signal(body):

    if pd.isna(body):
        return None

    text = " ".join(str(body).split()).lower()

    signals = [
        ("officially_applied_to", "officially applied to"),
        ("apply_for_the", "apply for the"),
        ("applying_to_the", "applying to the"),
        ("applying_for_the", "applying for the"),
        ("thank_you_for_applying_to_the", "thank you for applying to the"),
        ("thank_you_for_applying_for_the", "thank you for applying for the"),
        ("position_of", "position of"),
        ("position_at", "position at"),
        ("role_at", "role at"),
        ("role_with", "role with"),
        ("resume_for", "resume for"),
    ]

    for signal_name, phrase in signals:

        if phrase in text:
            return signal_name

    return None


compact_review["title_signal"] = (
    compact_review["body_preview"]
    .apply(detect_title_signal)
)

print()
print("=" * 70)
print("STRONG TITLE SIGNAL AUDIT")
print("=" * 70)

print(
    f"Jobs reviewed: "
    f"{len(compact_review)}"
)

print(
    f"Jobs with strong title signal: "
    f"{compact_review['title_signal'].notna().sum()}"
)

print(
    f"Jobs without strong title signal: "
    f"{compact_review['title_signal'].isna().sum()}"
)

print()
print("--- SIGNAL COUNTS ---")

print(
    compact_review["title_signal"]
    .value_counts(dropna=False)
    .to_string()
)

# --------------------------------------------------
# Inspect jobs with strong title signals
# --------------------------------------------------

print()
print("=" * 70)
print("STRONG TITLE SIGNAL JOBS")
print("=" * 70)

strong_signal_jobs = (
    compact_review[
        compact_review["title_signal"].notna()
    ][
        [
            "job_id",
            "company_name",
            "title_signal",
            "body_preview"
        ]
    ]
    .copy()
)

print(
    strong_signal_jobs.to_string(
        index=False
    )
)