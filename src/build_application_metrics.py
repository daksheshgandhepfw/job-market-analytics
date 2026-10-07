from pathlib import Path

import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

INPUT_FILE = Path(
    "data/processed/application_analysis.csv"
)

OUTPUT_FILE = Path(
    "data/processed/application_metrics.csv"
)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

df = pd.read_csv(
    INPUT_FILE
)


print("=== STAGE 5.2: BUILD APPLICATION METRICS ===")
print()

print(
    f"Applications loaded: "
    f"{len(df)}"
)


# --------------------------------------------------
# Convert dates
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
# Response indicator
# --------------------------------------------------

df["has_response"] = (
    df["response_status"]
    .eq("Responded")
    .astype(int)
)


# --------------------------------------------------
# Response time
# --------------------------------------------------

df["response_days"] = (
    df["first_response_date"]
    - df["application_date"]
).dt.days


# --------------------------------------------------
# Application date dimensions
# --------------------------------------------------

df["application_year"] = (
    df["application_date"]
    .dt.year
    .astype("Int64")
)

df["application_month"] = (
    df["application_date"]
    .dt.month
    .astype("Int64")
)

df["application_month_name"] = (
    df["application_date"]
    .dt.month_name()
)

df["application_year_month"] = (
    df["application_date"]
    .dt.to_period("M")
    .astype("string")
)

df["application_day_of_week"] = (
    df["application_date"]
    .dt.day_name()
)


# --------------------------------------------------
# Validation
# --------------------------------------------------

print()
print("--- RESPONSE METRICS ---")

print(
    f"Applications with response: "
    f"{df['has_response'].sum()}"
)

print(
    f"Applications without response: "
    f"{(df['has_response'] == 0).sum()}"
)

print(
    f"Applications with response_days: "
    f"{df['response_days'].notna().sum()}"
)

print(
    f"Applications missing response_days: "
    f"{df['response_days'].isna().sum()}"
)


# --------------------------------------------------
# Response-days quality checks
# --------------------------------------------------

print()
print("--- RESPONSE DAYS VALIDATION ---")

print(
    f"Negative response days: "
    f"{(df['response_days'] < 0).sum()}"
)

print(
    f"Zero-day responses: "
    f"{(df['response_days'] == 0).sum()}"
)

if df["response_days"].notna().any():

    print(
        f"Minimum response days: "
        f"{df['response_days'].min()}"
    )

    print(
        f"Maximum response days: "
        f"{df['response_days'].max()}"
    )

    print(
        f"Median response days: "
        f"{df['response_days'].median()}"
    )


# --------------------------------------------------
# Date-dimension validation
# --------------------------------------------------

print()
print("--- DATE DIMENSION VALIDATION ---")

print(
    f"Missing application dates: "
    f"{df['application_date'].isna().sum()}"
)

print(
    f"Missing application years: "
    f"{df['application_year'].isna().sum()}"
)

print(
    f"Missing application months: "
    f"{df['application_month'].isna().sum()}"
)

print(
    f"Missing year-month values: "
    f"{df['application_year_month'].isna().sum()}"
)

print(
    f"Missing day-of-week values: "
    f"{df['application_day_of_week'].isna().sum()}"
)


# --------------------------------------------------
# Monthly application counts
# --------------------------------------------------

print()
print("--- APPLICATIONS BY YEAR-MONTH ---")

monthly_counts = (
    df.dropna(
        subset=["application_year_month"]
    )
    ["application_year_month"]
    .value_counts()
    .sort_index()
)

print(
    monthly_counts.to_string()
)


# --------------------------------------------------
# Save
# --------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print("=" * 70)
print("APPLICATION METRICS DATASET CREATED")
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