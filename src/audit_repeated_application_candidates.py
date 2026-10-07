import pandas as pd

INPUT_FILE = "data/processed/final_enriched_job_emails.csv"
OUTPUT_FILE = "data/processed/repeated_application_candidates.txt"


def clean(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def main():
    df = pd.read_csv(INPUT_FILE)

    df["company_name"] = df["company_name"].fillna("").str.strip()
    df["job_title"] = df["job_title"].fillna("").str.strip()

    candidates = df[
        (df["company_name"] != "") &
        (df["job_title"] != "")
    ].copy()

    counts = (
        candidates
        .groupby(["company_name", "job_title"])
        .size()
        .reset_index(name="email_count")
    )

    repeated = counts[counts["email_count"] > 1].copy()

    repeated = repeated.sort_values(
        ["email_count", "company_name"],
        ascending=[False, True]
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

        f.write("=== REPEATED COMPANY + TITLE CANDIDATES ===\n\n")
        f.write(f"Repeated groups: {len(repeated)}\n")
        f.write(f"Emails in repeated groups: {repeated['email_count'].sum()}\n\n")

        for group_number, (_, group) in enumerate(
            repeated.iterrows(),
            start=1
        ):
            company = group["company_name"]
            title = group["job_title"]

            rows = candidates[
                (candidates["company_name"] == company) &
                (candidates["job_title"] == title)
            ].copy()

            rows["email_date"] = pd.to_datetime(
                rows["email_date"],
                errors="coerce"
            )

            rows = rows.sort_values("email_date")

            f.write("=" * 90 + "\n")
            f.write(f"GROUP {group_number}\n")
            f.write(f"Company: {company}\n")
            f.write(f"Job Title: {title}\n")
            f.write(f"Email Count: {len(rows)}\n\n")

            for _, row in rows.iterrows():

                f.write(f"Email ID: {clean(row.get('email_id'))}\n")
                f.write(f"Date: {clean(row.get('email_date'))}\n")
                f.write(f"Type: {clean(row.get('email_type'))}\n")
                f.write(
                    f"Reference ID: "
                    f"{clean(row.get('job_reference_id'))}\n"
                )
                f.write(f"Subject: {clean(row.get('subject'))}\n")
                f.write(f"Sender: {clean(row.get('sender'))}\n")

                body = clean(row.get("email_body"))
                f.write(f"Body Preview: {body[:500]}\n")
                f.write("-" * 70 + "\n")

            f.write("\n")

    print("Repeated company-title groups:", len(repeated))
    print(
        "Emails in repeated groups:",
        repeated["email_count"].sum()
    )
    print("Created:", OUTPUT_FILE)


if __name__ == "__main__":
    main()