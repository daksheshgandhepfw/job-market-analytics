import pandas as pd
import re
from pathlib import Path

INPUT_FILE = Path("data/processed/enriched_job_emails_with_titles.csv")
OUTPUT_FILE = Path("data/processed/body_title_candidate_audit.txt")


def clean_text(value):
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def clean_candidate(value):
    value = clean_text(value)

    # Remove common trailing punctuation
    value = value.strip(" .,:;-")

    return value


def extract_title_candidates(body):
    """
    Extract possible job titles from email bodies.

    IMPORTANT:
    These are only candidates for auditing.
    Nothing is written back to the dataset.
    """

    body = clean_text(body)

    if not body:
        return []

    patterns = [
        # "application for the Data Analyst role"
        r"\bapplication for the\s+(.+?)\s+role\b",

        # "application for the Data Analyst position"
        r"\bapplication for the\s+(.+?)\s+position\b",

        # "application for Data Analyst role"
        r"\bapplication for\s+(.+?)\s+role\b",

        # "application for Data Analyst position"
        r"\bapplication for\s+(.+?)\s+position\b",

        # "applied to the Data Analyst role at Company"
        r"\bapplied to the\s+(.+?)\s+role\s+at\b",

        # "applied to the Data Analyst at Company"
        r"\bapplied to the\s+(.+?)\s+at\b",

        # "applying to the Data Analyst role"
        r"\bapplying to the\s+(.+?)\s+role\b",

        # "apply for the Data Analyst at Company"
        r"\bapply for the\s+(.+?)\s+at\b",

        # "interest in the Data Analyst role"
        r"\binterest in the\s+(.+?)\s+role\b",

        # "interest in Data Analyst"
        # Limited by common sentence endings.
        r"\binterest in\s+(.+?)(?:\s+at\s+|\s+with\s+|[.!])",

        # "received your application for Data Analyst"
        r"\breceived your application for\s+(.+?)(?:\s+role\b|\s+position\b|[.!])",

        # "received your submission to the following position:
        # R041586 Intern - IT Data Science"
        r"\bsubmission to the following position:\s*(.+?)(?:\s+we\b|[.!])",

        # "online application for Engineering Intern-1
        # has successfully been received"
        r"\bonline application for\s+(.+?)\s+has successfully been received\b",

        # "submitting your application to 2026 Summer Software Engineer Internship at ITW"
        r"\bsubmitting your application to\s+(.+?)\s+at\b",

        # "submit your application for the Software Development Intern position"
        r"\bsubmit your application for the\s+(.+?)\s+position\b",

        # "application for Data Strategy Analyst."
        r"\bapplication for\s+(.+?)(?:\s+has\b|\s+was\b|\s+is\b|[.!])",
    ]

    candidates = []

    for pattern in patterns:
        for match in re.finditer(pattern, body, flags=re.IGNORECASE):
            candidate = clean_candidate(match.group(1))

            if not candidate:
                continue

            candidates.append(
                {
                    "candidate": candidate,
                    "matched_text": clean_text(match.group(0)),
                    "pattern": pattern,
                }
            )

    # Remove duplicate candidates from the same email
    unique = []
    seen = set()

    for item in candidates:
        key = item["candidate"].lower()

        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique


def get_context(body, matched_text, context_size=180):
    body = clean_text(body)

    index = body.lower().find(matched_text.lower())

    if index == -1:
        return ""

    start = max(0, index - context_size)
    end = min(len(body), index + len(matched_text) + context_size)

    return body[start:end]


df = pd.read_csv(INPUT_FILE)

missing_df = df[
    df["job_title"].fillna("").str.strip().eq("")
].copy()

output = []

output.append(f"Total records: {len(df)}")
output.append(f"Missing-title records: {len(missing_df)}")
output.append("")

emails_with_candidates = 0
total_candidates = 0

for _, row in missing_df.iterrows():

    body = clean_text(row.get("email_body", ""))

    candidates = extract_title_candidates(body)

    if not candidates:
        continue

    emails_with_candidates += 1
    total_candidates += len(candidates)

    output.append("=" * 100)
    output.append(f"Email ID: {row.get('email_id', '')}")
    output.append(f"Company: {row.get('company_name', '')}")
    output.append(f"Subject: {row.get('subject', '')}")
    output.append(f"Sender: {row.get('sender', '')}")
    output.append("")

    for number, item in enumerate(candidates, start=1):

        context = get_context(
            body,
            item["matched_text"]
        )

        output.append(f"Candidate {number}: {item['candidate']}")
        output.append(f"Matched Text: {item['matched_text']}")
        output.append("")
        output.append("CONTEXT:")
        output.append(context)
        output.append("")

output.insert(
    2,
    f"Missing-title emails with at least one candidate: {emails_with_candidates}"
)

output.insert(
    3,
    f"Total extracted candidates: {total_candidates}"
)

OUTPUT_FILE.write_text(
    "\n".join(output),
    encoding="utf-8"
)

print(f"Total records: {len(df)}")
print(f"Missing-title records: {len(missing_df)}")
print(
    f"Missing-title emails with candidate: "
    f"{emails_with_candidates}"
)
print(f"Total extracted candidates: {total_candidates}")
print(f"Audit written to: {OUTPUT_FILE}")