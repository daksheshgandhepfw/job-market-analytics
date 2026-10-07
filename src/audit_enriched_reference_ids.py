import pandas as pd

INPUT_FILE = "data/processed/enriched_job_reference_ids.csv"
OUTPUT_FILE = "data/processed/enriched_reference_id_audit.txt"


def clean(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def main():
    df = pd.read_csv(INPUT_FILE)

    # Only IDs newly recovered by our enrichment
    new_ids = df[
        df["job_reference_id_source"].isin(
            ["SUBJECT", "BODY", "BRACKET_CONTEXT"]
        )
    ].copy()

    # Sort to make review easier
    new_ids = new_ids.sort_values(
        ["job_reference_id_source", "company_name", "job_reference_id"]
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

        f.write("=== ENRICHED JOB REFERENCE ID AUDIT ===\n\n")
        f.write(f"Total newly recovered IDs: {len(new_ids)}\n\n")

        for _, row in new_ids.iterrows():

            f.write("=" * 90 + "\n")

            f.write(
                f"Email ID: {clean(row.get('email_id'))}\n"
            )

            f.write(
                f"Company: {clean(row.get('company_name'))}\n"
            )

            f.write(
                f"Job Title: {clean(row.get('job_title'))}\n"
            )

            f.write(
                f"Email Type: {clean(row.get('email_type'))}\n"
            )

            f.write(
                f"Recovered Reference ID: "
                f"{clean(row.get('job_reference_id'))}\n"
            )

            f.write(
                f"Source: "
                f"{clean(row.get('job_reference_id_source'))}\n"
            )

            f.write(
                f"Original Reference ID: "
                f"{clean(row.get('raw_job_reference_id'))}\n"
            )

            f.write(
                f"Subject: {clean(row.get('subject'))}\n"
            )

            body = clean(row.get("email_body"))

            f.write("\nBODY PREVIEW:\n")
            f.write(body[:1000])
            f.write("\n\n")

    print("New reference IDs audited:", len(new_ids))

    print("\nSource counts:")
    print(
        new_ids["job_reference_id_source"]
        .value_counts()
    )

    print("\nCreated:", OUTPUT_FILE)


if __name__ == "__main__":
    main()