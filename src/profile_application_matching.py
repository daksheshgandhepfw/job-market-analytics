import pandas as pd

INPUT_FILE = "data/processed/final_enriched_job_emails.csv"


def main():
    df = pd.read_csv(INPUT_FILE)

    # Normalize blanks for analysis only.
    for col in [
        "company_name",
        "job_title",
        "job_reference_id",
        "email_type",
    ]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    print("=== APPLICATION MATCHING PROFILE ===\n")

    print("Total job-related emails:", len(df))

    # ---------------------------------------------------------
    # Matching field availability
    # ---------------------------------------------------------

    has_company = df["company_name"] != ""
    has_title = df["job_title"] != ""
    has_reference = df["job_reference_id"] != ""

    print("\n--- FIELD AVAILABILITY ---")
    print("Company present:", has_company.sum())
    print("Job title present:", has_title.sum())
    print("Reference ID present:", has_reference.sum())

    print(
        "Company + title present:",
        (has_company & has_title).sum()
    )

    print(
        "Company + title + reference present:",
        (has_company & has_title & has_reference).sum()
    )

    # ---------------------------------------------------------
    # Email types
    # ---------------------------------------------------------

    print("\n--- EMAIL TYPES ---")
    print(df["email_type"].value_counts(dropna=False))

    # ---------------------------------------------------------
    # Reference ID analysis
    # ---------------------------------------------------------

    refs = df[has_reference]

    print("\n--- REFERENCE ID ANALYSIS ---")
    print("Emails with reference ID:", len(refs))
    print(
        "Unique reference IDs:",
        refs["job_reference_id"].nunique()
    )

    ref_counts = (
        refs.groupby("job_reference_id")
        .size()
        .sort_values(ascending=False)
    )

    repeated_refs = ref_counts[ref_counts > 1]

    print(
        "Reference IDs appearing in multiple emails:",
        len(repeated_refs)
    )

    print(
        "Emails belonging to repeated reference IDs:",
        repeated_refs.sum()
    )

    # ---------------------------------------------------------
    # Company + title analysis
    # ---------------------------------------------------------

    company_title = df[has_company & has_title].copy()

    pair_counts = (
        company_title
        .groupby(["company_name", "job_title"])
        .size()
        .sort_values(ascending=False)
    )

    repeated_pairs = pair_counts[pair_counts > 1]

    print("\n--- COMPANY + TITLE ANALYSIS ---")
    print(
        "Unique company-title pairs:",
        len(pair_counts)
    )

    print(
        "Company-title pairs appearing multiple times:",
        len(repeated_pairs)
    )

    print(
        "Emails belonging to repeated company-title pairs:",
        repeated_pairs.sum()
    )

    # ---------------------------------------------------------
    # Missing-title population
    # ---------------------------------------------------------

    missing_title = df[~has_title]

    print("\n--- MISSING TITLE EMAILS ---")
    print("Emails missing job title:", len(missing_title))

    print(
        "Missing-title emails WITH reference ID:",
        (missing_title["job_reference_id"] != "").sum()
    )

    print(
        "Missing-title emails WITHOUT reference ID:",
        (missing_title["job_reference_id"] == "").sum()
    )


if __name__ == "__main__":
    main()