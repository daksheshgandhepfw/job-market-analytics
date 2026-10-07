import pandas as pd


INPUT_FILE = "data/processed/applications_deduplicated.csv"


def main():

    df = pd.read_csv(INPUT_FILE)

    # Convert dates
    df["application_date"] = pd.to_datetime(
        df["application_date"],
        errors="coerce"
    )

    df["first_response_date"] = pd.to_datetime(
        df["first_response_date"],
        errors="coerce"
    )

    # Field availability
    application_date_present = (
        df["application_date"].notna().sum()
    )

    title_present = (
        df["job_title"]
        .fillna("")
        .str.strip()
        .ne("")
        .sum()
    )

    reference_present = (
        df["job_reference_id"]
        .fillna("")
        .str.strip()
        .ne("")
        .sum()
    )

    missing_title = len(df) - title_present
    missing_reference = len(df) - reference_present

    missing_both = (
        df["job_title"]
        .fillna("")
        .str.strip()
        .eq("")
        &
        df["job_reference_id"]
        .fillna("")
        .str.strip()
        .eq("")
    ).sum()

    # Rejection validation
    rejected = df[
        df["status"] == "Rejected"
    ]

    rejected_missing_response_date = (
        rejected[
            "first_response_date"
        ].isna().sum()
    )

    # Impossible date relationships
    impossible_dates = df[
        df["application_date"].notna()
        &
        df["first_response_date"].notna()
        &
        (
            df["first_response_date"]
            <
            df["application_date"]
        )
    ]

    # Application ID validation
    duplicate_application_ids = (
        df["application_id"]
        .duplicated()
        .sum()
    )

    print(
        "=== APPLICATION DATASET VALIDATION ==="
    )

    print(
        "\nTotal applications:",
        len(df)
    )

    print(
        "\n--- FIELD COMPLETENESS ---"
    )

    print(
        "Application date present:",
        application_date_present
    )

    print(
        "Application date missing:",
        len(df) - application_date_present
    )

    print(
        "Job title present:",
        title_present
    )

    print(
        "Job title missing:",
        missing_title
    )

    print(
        "Reference ID present:",
        reference_present
    )

    print(
        "Reference ID missing:",
        missing_reference
    )

    print(
        "Missing BOTH title and reference ID:",
        missing_both
    )

    print(
        "\n--- STATUS VALIDATION ---"
    )

    print(
        "Rejected applications:",
        len(rejected)
    )

    print(
        "Rejected applications missing "
        "first response date:",
        rejected_missing_response_date
    )
    
    rejected_without_response_date = rejected[
        rejected["first_response_date"].isna()
    ]

    if not rejected_without_response_date.empty:

        print(
            "\n--- REJECTED WITHOUT RESPONSE DATE ---"
        )

        print(
            rejected_without_response_date[
                [
                    "application_id",
                    "company_name",
                    "job_title",
                    "job_reference_id",
                    "application_date",
                    "email_count",
                    "email_ids"
                ]
            ].to_string(index=False)
        )

    print(
        "\n--- DATE VALIDATION ---"
    )

    print(
        "Applications where response date "
        "is before application date:",
        len(impossible_dates)
    )

    print(
        "\n--- ID VALIDATION ---"
    )

    print(
        "Duplicate application IDs:",
        duplicate_application_ids
    )

    # Show impossible cases only if they exist
    if not impossible_dates.empty:

        print(
            "\n--- IMPOSSIBLE DATE RECORDS ---"
        )

        print(
            impossible_dates[
                [
                    "application_id",
                    "company_name",
                    "job_title",
                    "application_date",
                    "first_response_date"
                ]
            ].to_string(index=False)
        )


if __name__ == "__main__":
    main()