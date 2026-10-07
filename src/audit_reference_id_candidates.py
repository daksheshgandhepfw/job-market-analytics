import pandas as pd
import re

INPUT_FILE = "data/processed/final_enriched_job_emails.csv"
OUTPUT_FILE = "data/processed/reference_id_candidates.txt"


def clean(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def extract_candidates(text):
    """
    Find strings that look like possible job/requisition IDs.
    AUDIT ONLY — nothing is automatically accepted.
    """

    if not text:
        return []

    patterns = [
        # R0248430, R139139, R-8129
        r"\bR-?\d{4,10}\b",

        # RQ4078036
        r"\bRQ-?\d{4,10}\b",

        # JR123456
        r"\bJR-?\d{4,10}\b",

        # REQ123456 / REQ-123456
        r"\bREQ-?\d{4,10}\b",

        # J2462394
        r"\bJ\d{5,10}\b",

        # Long standalone numeric IDs such as 2531393 / 26013283
        r"(?<![\d/.-])\b\d{6,9}\b(?![\d/.-])",
    ]

    found = []

    for pattern in patterns:
        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        for match in matches:
            match = match.strip()

            if match not in found:
                found.append(match)

    return found


def main():
    df = pd.read_csv(INPUT_FILE)

    records_with_candidates = 0
    records_without_existing_id = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

        f.write("=== JOB REFERENCE ID CANDIDATE AUDIT ===\n\n")
        f.write(f"Total records: {len(df)}\n\n")

        for _, row in df.iterrows():

            existing_id = clean(row.get("job_reference_id"))

            subject = clean(row.get("subject"))
            body = clean(row.get("email_body"))

            subject_candidates = extract_candidates(subject)
            body_candidates = extract_candidates(body)

            all_candidates = []

            for candidate in subject_candidates + body_candidates:
                if candidate not in all_candidates:
                    all_candidates.append(candidate)

            if not all_candidates:
                continue

            records_with_candidates += 1

            if not existing_id:
                records_without_existing_id += 1

            f.write("=" * 90 + "\n")
            f.write(f"Email ID: {clean(row.get('email_id'))}\n")
            f.write(f"Company: {clean(row.get('company_name'))}\n")
            f.write(f"Job Title: {clean(row.get('job_title'))}\n")
            f.write(f"Email Type: {clean(row.get('email_type'))}\n")
            f.write(f"Existing Reference ID: {existing_id}\n")

            f.write(
                "Subject Candidates: "
                + ", ".join(subject_candidates)
                + "\n"
            )

            f.write(
                "Body Candidates: "
                + ", ".join(body_candidates)
                + "\n"
            )

            f.write(f"Subject: {subject}\n")

            f.write("\nBODY PREVIEW:\n")
            f.write(body[:800] + "\n\n")

    print("Total records:", len(df))
    print(
        "Records containing possible reference IDs:",
        records_with_candidates
    )
    print(
        "Records with candidates but no existing reference ID:",
        records_without_existing_id
    )
    print("Created:", OUTPUT_FILE)


if __name__ == "__main__":
    main()