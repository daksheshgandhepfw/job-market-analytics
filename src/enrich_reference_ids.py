import pandas as pd
import re

INPUT_FILE = "data/processed/final_enriched_job_emails.csv"
OUTPUT_FILE = "data/processed/enriched_job_reference_ids.csv"


def clean(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_reference_id(value):
    """
    Normalize whitespace only.
    Preserve meaningful hyphens such as R-252243.
    """
    value = clean(value)
    return re.sub(r"\s+", "", value)


def extract_from_subject(subject, company):
    """
    Extract reference IDs from strong subject-line patterns.
    """

    subject = clean(subject)
    company = clean(company).lower()

    if not subject:
        return "", "MISSING"

    # Strong prefixed IDs
    prefixed_patterns = [
        r"\b(RQ-?\d{4,10})\b",
        r"\b(REQ-?\d{4,10})\b",
        r"\b(JR-?\d{4,10})\b",
        r"\b(R-\d{4,10})\b",
        r"\b(R\d{5,10})\b",
        r"\b(J\d{5,10})\b",
    ]

    for pattern in prefixed_patterns:
        match = re.search(
            pattern,
            subject,
            flags=re.IGNORECASE
        )

        if match:
            return (
                normalize_reference_id(match.group(1)),
                "SUBJECT"
            )

    # American Express
    if company in {"amex", "american express"}:
        match = re.search(
            r"\s-\s(\d{8})\s*$",
            subject
        )

        if match:
            return match.group(1), "SUBJECT"

    # Providence
    if "providence" in company:
        match = re.search(
            r"\s-\s(\d{6,8})\s*$",
            subject
        )

        if match:
            return match.group(1), "SUBJECT"

    return "", "MISSING"


def extract_from_body(body, company):
    """
    Extract IDs only when body context strongly indicates
    that the value belongs to the job/requisition.
    """

    body = clean(body)
    company = clean(company).lower()

    if not body:
        return "", "MISSING"

    # ---------------------------------------------------------
    # 1. Alcon extended format MUST come before generic R-
    # Example: R-2026-49480
    # ---------------------------------------------------------

    if "alcon" in company:
        match = re.search(
            r"\b(R-\d{4}-\d{4,8})\b",
            body,
            flags=re.IGNORECASE
        )

        if match:
            return (
                normalize_reference_id(match.group(1)),
                "BODY"
            )

    # ---------------------------------------------------------
    # 2. Strong prefixed IDs
    # ---------------------------------------------------------

    prefixed_patterns = [
        r"\b(RQ-?\d{4,10})\b",
        r"\b(REQ-?\d{4,10})\b",
        r"\b(JR-?\d{4,10})\b",
        r"\b(R-\d{4,10})\b",
        r"\b(R\d{5,10})\b",
        r"\b(J\d{5,10})\b",
    ]

    for pattern in prefixed_patterns:
        match = re.search(
            pattern,
            body,
            flags=re.IGNORECASE
        )

        if match:
            return (
                normalize_reference_id(match.group(1)),
                "BODY"
            )

    # ---------------------------------------------------------
    # 3. Amazon
    # Example: ID: 10557661
    # ---------------------------------------------------------

    if "amazon" in company:
        match = re.search(
            r"\bID:\s*(\d{5,10})\b",
            body,
            flags=re.IGNORECASE
        )

        if match:
            return match.group(1), "BODY"

    # ---------------------------------------------------------
    # 4. RTX / Raytheon
    # Example: position of 01870647 Software Engineer
    # ---------------------------------------------------------

    if company == "rtx" or "raytheon" in company:
        match = re.search(
            r"position of\s+(\d{7,9})\b",
            body,
            flags=re.IGNORECASE
        )

        if match:
            return match.group(1), "BODY"

    # ---------------------------------------------------------
    # 5. Emory
    # Example: requisition 165195 - Data Analyst II
    # ---------------------------------------------------------

    if "emory" in company:
        match = re.search(
            r"\brequisition\s+(\d{5,9})\b",
            body,
            flags=re.IGNORECASE
        )

        if match:
            return match.group(1), "BODY"

    # ---------------------------------------------------------
    # 6. State of South Carolina
    # Example: (12601701) position
    # ---------------------------------------------------------

    if "state of south carolina" in company:
        match = re.search(
            r"\((\d{6,10})\)\s+position\b",
            body,
            flags=re.IGNORECASE
        )

        if match:
            return match.group(1), "BODY"

    # ---------------------------------------------------------
    # 7. Howmet
    # ---------------------------------------------------------

    if "howmet" in company:
        match = re.search(
            r"\bposition of .{0,100}?-\s*(\d{5,9})\b",
            body,
            flags=re.IGNORECASE
        )

        if not match:
            match = re.search(
                r"\bRe:\s*.+?[-–]\s*(\d{5,9})\b",
                body,
                flags=re.IGNORECASE
            )

        if match:
            return match.group(1), "BODY"

    # ---------------------------------------------------------
    # 8. Compass
    # Example: (1490988) with
    # ---------------------------------------------------------

    if "compass" in company:
        match = re.search(
            r"\((\d{6,9})\s*\)\s+with\b",
            body,
            flags=re.IGNORECASE
        )

        if match:
            return match.group(1), "BODY"

    # ---------------------------------------------------------
    # 9. Pella
    # Example:
    # role of Data Engineer Intern - Summer 2027 - 253304!
    # ---------------------------------------------------------

    if "pella" in company:
        match = re.search(
            r"role of .{0,150}?-\s*(\d{5,9})\s*!",
            body,
            flags=re.IGNORECASE
        )

        if match:
            return match.group(1), "BODY"

    # ---------------------------------------------------------
    # 10. ATS bracket IDs
    # Example: [316545]
    # ---------------------------------------------------------

    bracket_match = re.search(
        r"\[(\d{5,9})\]",
        body
    )

    if bracket_match:
        return (
            bracket_match.group(1),
            "BRACKET_CONTEXT"
        )

    return "", "MISSING"


def main():
    df = pd.read_csv(INPUT_FILE)

    # Preserve original reference ID
    df["raw_job_reference_id"] = df["job_reference_id"]

    final_ids = []
    sources = []

    newly_enriched = 0

    for _, row in df.iterrows():

        existing = normalize_reference_id(
            row.get("job_reference_id")
        )

        # Existing reference IDs always win
        if existing:
            final_ids.append(existing)
            sources.append("EXISTING")
            continue

        company = clean(
            row.get("company_name")
        )

        subject = clean(
            row.get("subject")
        )

        body = clean(
            row.get("email_body")
        )

        # Try subject first
        reference_id, source = extract_from_subject(
            subject,
            company
        )

        # If nothing found, try body
        if not reference_id:
            reference_id, source = extract_from_body(
                body,
                company
            )

        if reference_id:
            newly_enriched += 1
            final_ids.append(reference_id)
            sources.append(source)

        else:
            final_ids.append("")
            sources.append("MISSING")

    df["job_reference_id"] = final_ids
    df["job_reference_id_source"] = sources

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    present = (
        df["job_reference_id"] != ""
    ).sum()

    missing = (
        df["job_reference_id"] == ""
    ).sum()

    print("Total records:", len(df))

    print(
        "Existing reference IDs:",
        (
            df["job_reference_id_source"]
            == "EXISTING"
        ).sum()
    )

    print(
        "New reference IDs recovered:",
        newly_enriched
    )

    print()

    print(
        "Reference IDs present after enrichment:",
        present
    )

    print(
        "Reference IDs missing:",
        missing
    )

    print(
        "Reference ID completeness:",
        f"{present / len(df) * 100:.1f}%"
    )

    print("\nReference ID sources:")

    print(
        df["job_reference_id_source"]
        .value_counts()
    )

    print(
        "\nCreated:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()