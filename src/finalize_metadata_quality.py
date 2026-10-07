import pandas as pd

INPUT_FILE = "data/processed/enriched_job_emails_with_body_titles.csv"
OUTPUT_FILE = "data/processed/final_enriched_job_emails.csv"


CORRECTIONS = {
    "1a063894d113d3dc": {
        "company_name": "Amex"
    },

    "1a0637e9eb9d40d4": {
        "company_name": "Amex"
    },

    "1a0636b74b2907b7": {
        "company_name": "Johnson & Johnson"
    },

    "19ff23ce275a61d5": {
        "company_name": "Barclays"
    },
    
    "1a07297ae41321bf": {
        "company_name": "CNA",
    },

    "1a06dc872cc7a68b": {
        "company_name": "York Space Systems",
    },

    "1a06d1933b93f5e7": {
        "company_name": "Oddball",
    },

    "1a06d173992dd11f": {
        "company_name": "SNC",
    },

    "1a06d1034bd1c68f": {
        "company_name": "INDUS Technology, Inc.",
    },

    "1a05e4f450e28767": {
        "company_name": "Ipsos",
    },

    "19ff296c01de1fa4": {
        "company_name": "Curant Health Georgia LLC",
    },

    "19ff289a6f309e5f": {
        "company_name": "Grande",
        "job_title": "Data Analytics Science Intern",
    },

    "19fe2d391f802f12": {
        "company_name": "Ruby Labs",
    },

    "19d4a0bee106c876": {
        "company_name": "St. Luke's University Health Network",
        "job_title": "Information Technology Intern (Open)",
        "job_reference_id": "R139139",
    },

    "19d187e2d914a333": {
        "company_name": "AFL Telecommunications LLC",
    },

    "19c68804d6dffb4b": {
        "company_name": "SiriusXM",
    },
}


def main():
    df = pd.read_csv(INPUT_FILE)

    corrected = 0

    for email_id, changes in CORRECTIONS.items():

        mask = df["email_id"].astype(str) == email_id

        if mask.sum() != 1:
            print(
                f"WARNING: {email_id} matched {mask.sum()} records "
                f"instead of exactly 1."
            )
            continue

        for column, value in changes.items():
            df.loc[mask, column] = value

        # Preserve provenance.
        if "company_name" in changes:
            df.loc[mask, "company_source"] = "MANUAL_VERIFIED"

        if "job_title" in changes:
            df.loc[mask, "job_title_source"] = "MANUAL_VERIFIED"

        corrected += 1

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Total records: {len(df)}")
    print(f"Records corrected: {corrected}")
    print(f"Created: {OUTPUT_FILE}")

    print()
    print("Company missing:", df["company_name"].isna().sum())
    print("Job title missing:", df["job_title"].isna().sum())


if __name__ == "__main__":
    main()