from pathlib import Path

import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

INPUT_FILE = Path(
    "data/processed/application_metrics.csv"
)

OUTPUT_FILE = Path(
    "data/processed/applications_final.csv"
)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)


print("=== STAGE 5.5: BUILD FINAL APPLICATION DATASET ===")
print()

print(
    f"Applications loaded: "
    f"{len(df)}"
)


# --------------------------------------------------
# Convert date fields
# --------------------------------------------------

df["application_date"] = pd.to_datetime(
    df["application_date"],
    errors="coerce"
)

df["first_response_date"] = pd.to_datetime(
    df["first_response_date"],
    errors="coerce"
)


# --------------------------------------------------
# Business-facing outcome fields
# --------------------------------------------------

df["has_rejection"] = (
    df["status"]
    .eq("Rejected")
    .astype(int)
)


df["days_to_rejection"] = (
    df["first_response_date"]
    - df["application_date"]
).dt.days


# Only rejected applications should have
# days_to_rejection values.
df.loc[
    df["has_rejection"].eq(0),
    "days_to_rejection"
] = pd.NA


# --------------------------------------------------
# Final column order
# --------------------------------------------------

FINAL_COLUMNS = [
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
    "has_response",
    "has_rejection",
    "response_days",
    "days_to_rejection",
    "application_year",
    "application_month",
    "application_month_name",
    "application_year_month",
    "application_day_of_week",
    "email_count",
    "email_ids",
]


final = df[
    FINAL_COLUMNS
].copy()


# --------------------------------------------------
# Core validation
# --------------------------------------------------

print()
print("--- CORE VALIDATION ---")

print(
    f"Rows: "
    f"{len(final)}"
)

print(
    f"Unique application IDs: "
    f"{final['application_id'].nunique()}"
)

print(
    f"Duplicate application IDs: "
    f"{final['application_id'].duplicated().sum()}"
)

print(
    f"Unique job IDs: "
    f"{final['job_id'].nunique()}"
)

print(
    f"Missing job IDs: "
    f"{final['job_id'].isna().sum()}"
)


# --------------------------------------------------
# Rejection validation
# --------------------------------------------------

print()
print("--- REJECTION VALIDATION ---")

print(
    f"Observed rejections: "
    f"{final['has_rejection'].sum()}"
)

print(
    f"No observed rejection: "
    f"{final['has_rejection'].eq(0).sum()}"
)

print(
    f"Rejected status count: "
    f"{final['status'].eq('Rejected').sum()}"
)

print(
    f"Responded count: "
    f"{final['response_status'].eq('Responded').sum()}"
)

print(
    "has_rejection matches Rejected status: "
    f"{final['has_rejection'].eq(final['status'].eq('Rejected').astype(int)).all()}"
)


# --------------------------------------------------
# Days-to-rejection validation
# --------------------------------------------------

print()
print("--- DAYS TO REJECTION VALIDATION ---")

print(
    f"Measurable days-to-rejection: "
    f"{final['days_to_rejection'].notna().sum()}"
)

print(
    f"Missing days-to-rejection: "
    f"{final['days_to_rejection'].isna().sum()}"
)

print(
    f"Negative days-to-rejection: "
    f"{(final['days_to_rejection'] < 0).sum()}"
)

print(
    f"Non-rejected applications with days-to-rejection: "
    f"{(
        final['has_rejection'].eq(0)
        & final['days_to_rejection'].notna()
    ).sum()}"
)

if final["days_to_rejection"].notna().any():

    print(
        f"Minimum days-to-rejection: "
        f"{final['days_to_rejection'].min()}"
    )

    print(
        f"Maximum days-to-rejection: "
        f"{final['days_to_rejection'].max()}"
    )

    print(
        f"Median days-to-rejection: "
        f"{final['days_to_rejection'].median()}"
    )


# --------------------------------------------------
# Date coverage
# --------------------------------------------------

print()
print("--- DATE COVERAGE ---")

print(
    f"Applications with known application date: "
    f"{final['application_date'].notna().sum()}"
)

print(
    f"Applications missing application date: "
    f"{final['application_date'].isna().sum()}"
)

print(
    f"Rejections with known application date: "
    f"{(
        final['has_rejection'].eq(1)
        & final['application_date'].notna()
    ).sum()}"
)


# --------------------------------------------------
# Save
# --------------------------------------------------

final.to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print("=" * 70)
print("FINAL APPLICATION DATASET CREATED")
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