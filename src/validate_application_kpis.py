from pathlib import Path

import pandas as pd


# --------------------------------------------------
# File path
# --------------------------------------------------

INPUT_FILE = Path(
    "data/processed/application_metrics.csv"
)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)


print("=== STAGE 5.3: APPLICATION KPI VALIDATION ===")
print()

print(f"Applications loaded: {len(df)}")


# --------------------------------------------------
# Basic KPIs
# --------------------------------------------------

total_applications = df["application_id"].nunique()

unique_jobs = df["job_id"].nunique()

unique_companies = df["company_name"].nunique()

responses = df["has_response"].sum()

no_responses = (
    df["has_response"]
    .eq(0)
    .sum()
)

rejections = (
    df["status"]
    .eq("Rejected")
    .sum()
)


# --------------------------------------------------
# Rates
# --------------------------------------------------

response_rate = (
    responses / total_applications * 100
)

rejection_rate = (
    rejections / total_applications * 100
)


# --------------------------------------------------
# Response-time KPI
# --------------------------------------------------

response_time_sample = (
    df["response_days"]
    .notna()
    .sum()
)

median_response_days = (
    df["response_days"]
    .median()
)


# --------------------------------------------------
# Print core KPIs
# --------------------------------------------------

print()
print("--- CORE KPIs ---")

print(
    f"Total applications: "
    f"{total_applications}"
)

print(
    f"Unique jobs: "
    f"{unique_jobs}"
)

print(
    f"Unique companies: "
    f"{unique_companies}"
)

print(
    f"Responses: "
    f"{responses}"
)

print(
    f"No responses: "
    f"{no_responses}"
)

print(
    f"Response rate: "
    f"{response_rate:.2f}%"
)

print(
    f"Rejections: "
    f"{rejections}"
)

print(
    f"Rejection rate: "
    f"{rejection_rate:.2f}%"
)

print(
    f"Median response days: "
    f"{median_response_days}"
)

print(
    f"Response-time sample size: "
    f"{response_time_sample}"
)


# --------------------------------------------------
# Role-category KPIs
# --------------------------------------------------

role_kpis = (
    df.groupby(
        "role_category",
        dropna=False
    )
    .agg(
        applications=(
            "application_id",
            "count"
        ),
        responses=(
            "has_response",
            "sum"
        )
    )
    .reset_index()
)


role_kpis["response_rate"] = (
    role_kpis["responses"]
    / role_kpis["applications"]
    * 100
)


role_kpis = role_kpis.sort_values(
    "applications",
    ascending=False
)


print()
print("--- KPIs BY ROLE CATEGORY ---")

print(
    role_kpis.to_string(
        index=False,
        formatters={
            "response_rate": lambda x: f"{x:.2f}%"
        }
    )
)


# --------------------------------------------------
# Career-level KPIs
# --------------------------------------------------

career_kpis = (
    df.groupby(
        "career_level",
        dropna=False
    )
    .agg(
        applications=(
            "application_id",
            "count"
        ),
        responses=(
            "has_response",
            "sum"
        )
    )
    .reset_index()
)


career_kpis["response_rate"] = (
    career_kpis["responses"]
    / career_kpis["applications"]
    * 100
)


career_kpis = career_kpis.sort_values(
    "applications",
    ascending=False
)


print()
print("--- KPIs BY CAREER LEVEL ---")

print(
    career_kpis.to_string(
        index=False,
        formatters={
            "response_rate": lambda x: f"{x:.2f}%"
        }
    )
)


# --------------------------------------------------
# Monthly KPIs
# --------------------------------------------------

dated = df.dropna(
    subset=["application_year_month"]
).copy()


monthly_kpis = (
    dated.groupby(
        "application_year_month"
    )
    .agg(
        applications=(
            "application_id",
            "count"
        ),
        responses=(
            "has_response",
            "sum"
        )
    )
    .reset_index()
)


monthly_kpis["response_rate"] = (
    monthly_kpis["responses"]
    / monthly_kpis["applications"]
    * 100
)


monthly_kpis = monthly_kpis.sort_values(
    "application_year_month"
)


print()
print("--- KPIs BY APPLICATION MONTH ---")

print(
    monthly_kpis.to_string(
        index=False,
        formatters={
            "response_rate": lambda x: f"{x:.2f}%"
        }
    )
)


# --------------------------------------------------
# Sanity checks
# --------------------------------------------------

print()
print("--- KPI SANITY CHECKS ---")

print(
    "Applications = responses + no responses: "
    f"{total_applications == responses + no_responses}"
)

print(
    "Role applications sum to total: "
    f"{role_kpis['applications'].sum() == total_applications}"
)

print(
    "Career-level applications sum to total: "
    f"{career_kpis['applications'].sum() == total_applications}"
)

print(
    "Monthly applications sum to applications with known date: "
    f"{monthly_kpis['applications'].sum() == df['application_date'].notna().sum()}"
)

print(
    f"Applications with known date: "
    f"{df['application_date'].notna().sum()}"
)

print(
    f"Applications represented in monthly KPIs: "
    f"{monthly_kpis['applications'].sum()}"
)