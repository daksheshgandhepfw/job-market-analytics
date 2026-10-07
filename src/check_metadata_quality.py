import pandas as pd
import re

INPUT_FILE = "data/processed/final_enriched_job_emails.csv"
OUTPUT_FILE = "data/processed/metadata_quality_audit.txt"


def clean(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def suspicious_company(company):
    company = clean(company)

    if not company:
        return True

    lower = company.lower()

    suspicious_terms = [
        "data analyst",
        "data engineer",
        "software engineer",
        "software developer",
        "machine learning",
        "intern",
        "application received",
        "thank you for applying",
        "opportunities at",
        "talent acquisition",
        "we wish you",
    ]

    if any(term in lower for term in suspicious_terms):
        return True

    # Likely location accidentally stored as company.
    if re.fullmatch(r".+,\s*[A-Z]{2}", company):
        return True

    return False


def suspicious_title(title):
    title = clean(title)

    if not title:
        return False

    lower = title.lower()

    suspicious_terms = [
        "thank you for",
        "thanks for",
        "has been received",
        "application received",
        "your application",
        "we received",
        "we have received",
        "career opportunities",
        "employment and",
        "qualifications align",
    ]

    return any(term in lower for term in suspicious_terms)


def main():
    df = pd.read_csv(INPUT_FILE)

    flagged = []

    for _, row in df.iterrows():

        reasons = []

        company = clean(row.get("company_name"))
        title = clean(row.get("job_title"))
        reference = clean(row.get("job_reference_id"))

        if suspicious_company(company):
            reasons.append("SUSPICIOUS_COMPANY")

        if suspicious_title(title):
            reasons.append("SUSPICIOUS_TITLE")

        # Same value leaking across fields.
        if company and title and company.lower() == title.lower():
            reasons.append("COMPANY_EQUALS_TITLE")

        # Reference ID should not look like prose.
        if reference and len(reference.split()) > 5:
            reasons.append("SUSPICIOUS_REFERENCE_ID")

        if reasons:
            flagged.append((row, reasons))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

        f.write("=== FINAL METADATA QUALITY AUDIT ===\n\n")

        f.write(f"Total JOB_RELATED emails: {len(df)}\n")
        f.write(f"Flagged records: {len(flagged)}\n\n")

        for row, reasons in flagged:

            f.write("=" * 80 + "\n")

            f.write(f"Email ID: {clean(row.get('email_id'))}\n")
            f.write(f"Reasons: {', '.join(reasons)}\n")
            f.write(f"Company: {clean(row.get('company_name'))}\n")
            f.write(f"Company Source: {clean(row.get('company_source'))}\n")
            f.write(f"Job Title: {clean(row.get('job_title'))}\n")
            f.write(f"Job Title Source: {clean(row.get('job_title_source'))}\n")
            f.write(f"Reference ID: {clean(row.get('job_reference_id'))}\n")
            f.write(f"Sender: {clean(row.get('sender'))}\n")
            f.write(f"Subject: {clean(row.get('subject'))}\n")

            body = clean(row.get("email_body"))

            f.write("\nBODY PREVIEW:\n")
            f.write(body[:1000] + "\n\n")

    print(f"Total records: {len(df)}")
    print(f"Flagged records: {len(flagged)}")
    print(f"Created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()