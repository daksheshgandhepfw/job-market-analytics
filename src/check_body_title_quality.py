import pandas as pd

INPUT_FILE = "data/processed/enriched_job_emails_with_body_titles.csv"
OUTPUT_FILE = "data/processed/body_title_quality_audit.txt"


def clean(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def main():
    df = pd.read_csv(INPUT_FILE)

    body_titles = df[
        df["job_title_source"].fillna("").eq("BODY")
    ].copy()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

        f.write("=== BODY-DERIVED JOB TITLE AUDIT ===\n\n")
        f.write(f"Total records: {len(df)}\n")
        f.write(f"BODY-derived titles: {len(body_titles)}\n\n")

        for _, row in body_titles.iterrows():

            f.write("-" * 80 + "\n")

            f.write(f"Email ID: {clean(row.get('email_id'))}\n")
            f.write(f"Company: {clean(row.get('company_name'))}\n")
            f.write(f"Subject: {clean(row.get('subject'))}\n")
            f.write(f"Extracted Title: {clean(row.get('job_title'))}\n")
            f.write(f"Raw Title: {clean(row.get('raw_job_title'))}\n")

            body = clean(row.get("email_body"))

            # Show enough body context to verify the extraction.
            f.write("\nBODY PREVIEW:\n")
            f.write(body[:1200] + "\n\n")

    print(f"BODY-derived titles audited: {len(body_titles)}")
    print(f"Created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()