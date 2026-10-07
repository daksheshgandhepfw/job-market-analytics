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


print("=== STAGE 5.4: OUTCOME SEMANTICS VALIDATION ===")
print()

print(f"Applications loaded: {len(df)}")


# --------------------------------------------------
# Inspect source status fields
# --------------------------------------------------

print()
print("--- STATUS DISTRIBUTION ---")

print(
    df["status"]
    .value_counts(dropna=False)
    .to_string()
)


print()
print("--- RESPONSE STATUS DISTRIBUTION ---")

print(
    df["response_status"]
    .value_counts(dropna=False)
    .to_string()
)


# --------------------------------------------------
# Cross-tab status vs response status
# --------------------------------------------------

print()
print("--- STATUS VS RESPONSE STATUS ---")

status_cross_tab = pd.crosstab(
    df["status"],
    df["response_status"],
    dropna=False
)

print(
    status_cross_tab.to_string()
)


# --------------------------------------------------
# Inspect all responded applications
# --------------------------------------------------

responded = df[
    df["response_status"].eq("Responded")
].copy()


print()
print("--- RESPONDED APPLICATION VALIDATION ---")

print(
    f"Responded applications: "
    f"{len(responded)}"
)

print(
    f"Responded applications with status Rejected: "
    f"{responded['status'].eq('Rejected').sum()}"
)

print(
    f"Responded applications with non-Rejected status: "
    f"{(~responded['status'].eq('Rejected')).sum()}"
)

print(
    f"Responded applications with first response date: "
    f"{responded['first_response_date'].notna().sum()}"
)


# --------------------------------------------------
# Inspect any contradictions
# --------------------------------------------------

contradictions = responded[
    ~responded["status"].eq("Rejected")
].copy()


print()
print("--- POTENTIAL CONTRADICTIONS ---")

print(
    f"Responded but not Rejected: "
    f"{len(contradictions)}"
)

if len(contradictions) > 0:

    print()

    print(
        contradictions[
            [
                "application_id",
                "company_name",
                "job_title_clean",
                "status",
                "response_status",
                "first_response_date"
            ]
        ]
        .to_string(index=False)
    )


# --------------------------------------------------
# Reverse check:
# every rejection should have a response
# --------------------------------------------------

rejected = df[
    df["status"].eq("Rejected")
].copy()


print()
print("--- REJECTION VALIDATION ---")

print(
    f"Rejected applications: "
    f"{len(rejected)}"
)

print(
    f"Rejected with response_status Responded: "
    f"{rejected['response_status'].eq('Responded').sum()}"
)

print(
    f"Rejected with first response date: "
    f"{rejected['first_response_date'].notna().sum()}"
)

print(
    f"Rejected without first response date: "
    f"{rejected['first_response_date'].isna().sum()}"
)


# --------------------------------------------------
# Response-time availability among rejections
# --------------------------------------------------

print()
print("--- REJECTION RESPONSE-TIME COVERAGE ---")

print(
    f"Rejected applications with application date: "
    f"{rejected['application_date'].notna().sum()}"
)

print(
    f"Rejected applications with response date: "
    f"{rejected['first_response_date'].notna().sum()}"
)

print(
    f"Rejected applications with measurable response_days: "
    f"{rejected['response_days'].notna().sum()}"
)


# --------------------------------------------------
# Final semantic check
# --------------------------------------------------

all_responses_are_rejections = (
    responded["status"]
    .eq("Rejected")
    .all()
)

all_rejections_are_responses = (
    rejected["response_status"]
    .eq("Responded")
    .all()
)


print()
print("--- FINAL SEMANTIC CHECK ---")

print(
    "All Responded records are Rejected: "
    f"{all_responses_are_rejections}"
)

print(
    "All Rejected records are Responded: "
    f"{all_rejections_are_responses}"
)