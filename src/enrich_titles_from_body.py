import pandas as pd
import re

INPUT_FILE = "data/processed/enriched_job_emails_with_titles.csv"
OUTPUT_FILE = "data/processed/enriched_job_emails_with_body_titles.csv"


def clean_text(value):
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def clean_candidate(value):
    value = clean_text(value)

    # Remove surrounding punctuation/spacing.
    value = value.strip(" -–—:;,.")

    # Remove generic leading possessive/article.
    value = re.sub(
        r"^(?:our|the)\s+",
        "",
        value,
        flags=re.IGNORECASE,
    ).strip()

    # Remove confirmation prose accidentally captured after the title.
    value = re.sub(
        r"\s+has\s+successfully\s+been\s+received.*$",
        "",
        value,
        flags=re.IGNORECASE,
    ).strip()

    # Remove trailing "position".
    value = re.sub(
        r"\s+position$",
        "",
        value,
        flags=re.IGNORECASE,
    ).strip()

    # Remove employer tail: "... at Company"
    value = re.sub(
        r"\s+at\s+[^,.!?]+$",
        "",
        value,
        flags=re.IGNORECASE,
    ).strip()

    # Remove trailing standalone numeric requisition IDs.
    value = re.sub(
        r"\s+\d{4,8}$",
        "",
        value,
    ).strip()

    return value


def is_valid_title(title):
    title = clean_candidate(title)

    if not title:
        return False

    words = title.split()

    # Conservative limits.
    if len(title) < 3:
        return False

    if len(words) > 18:
        return False

    bad_exact = {
        "job",
        "role",
        "the",
        "employment",
        "our",
        "position",
        "opportunity",
        "application",
        "your application",
        "this role",
        "this position",
        "employment",
        "employment opportunities",
        "career opportunities",
    }

    if title.lower() in bad_exact:
        return False

    bad_fragments = [
        "thank you for",
        "thanks for",
        "your interest",
        "we received",
        "we have received",
        "has been received",
        "application has",
        "application was",
        "click here",
        "http://",
        "https://",
         "employment and will contact",
        "qualifications align with",
        "current needs",
    ]

    lower = title.lower()

    if any(fragment in lower for fragment in bad_fragments):
        return False

    return True


def extract_title_from_body(body):
    body = clean_text(body)

    if not body:
        return ""

    patterns = [
        # "application for the position of Data Analyst ..."
        (
            r"application\s+for\s+the\s+position\s+of\s+(.+?)"
            r"(?=\s+has\s+been\s+received|\s+and\s+are\s+currently|"
            r"\s+and\s+are\s+thrilled|[.!?]|$)"
        ),

        # "application for the position 'Information Technology Intern '"
        (
            r"application\s+for\s+the\s+position\s+[\"'](.+?)[\"']"
        ),

        # "application for our Data Engineer opportunity"
        (
            r"application\s+for\s+our\s+(.+?)\s+opportunity\b"
        ),

        # "application for our X position"
        (
            r"application\s+for\s+our\s+(.+?)\s+position\b"
        ),

        # "application for the X role"
        (
            r"(?:application|applying)\s+for\s+the\s+(.+?)\s+role\b"
        ),

        # "application for the X position"
        (
            r"application\s+for\s+the\s+(.+?)\s+position\b"
        ),

        # "application to the X position"
        (
            r"application\s+to\s+the\s+(.+?)\s+position\b"
        ),

        # "application to X position"
        (
            r"application\s+to\s+(.+?)\s+position\b"
        ),

        # "application for X opening and..."
        (
            r"application\s+for\s+(?:the\s+)?(.+?)\s+opening\b"
        ),

        # "application for X. What happens..."
        (
            r"application\s+for\s+(?:the\s+)?(.+?)"
            r"(?=\.\s+(?:What|We|Your|If|Thank)|[!?]|$)"
        ),

        # "application for X role"
        (
            r"application\s+for\s+(?:the\s+)?(.+?)\s+role\b"
        ),

        # "submission to the following position: R123 TITLE"
        (
            r"submission\s+to\s+the\s+following\s+position:\s*"
            r"(.+?)(?=\s+We\b|\s+Our\b|\s+Your\b|[.!?]|$)"
        ),

        # "application to X at Company"
        (
            r"application\s+to\s+(?:the\s+)?(.+?)\s+at\s+.+?"
            r"(?=[.!?]|$)"
        ),
    ]

    for pattern in patterns:
        match = re.search(pattern, body, flags=re.IGNORECASE)

        if not match:
            continue

        candidate = clean_candidate(match.group(1))

        # Remove leading requisition IDs:
        # R041586, R-252243, JR12345, REQ12345, etc.
        candidate = re.sub(
            r"^(?:R|JR|REQ)[-_]?[A-Z0-9-]+\s+",
            "",
            candidate,
            flags=re.IGNORECASE,
        ).strip()

        # Remove unnecessary leading article.
        candidate = re.sub(
            r"^the\s+",
            "",
            candidate,
            flags=re.IGNORECASE,
        ).strip()

        if is_valid_title(candidate):
            return candidate

    return ""


def main():
    df = pd.read_csv(INPUT_FILE)

    recovered = 0

    for index, row in df.iterrows():

        # Never overwrite titles already accepted.
        if str(row.get("job_title_source", "")).strip() != "MISSING":
            continue

        candidate = extract_title_from_body(row.get("email_body", ""))

        if not candidate:
            continue

        df.at[index, "job_title"] = candidate
        df.at[index, "job_title_source"] = "BODY"

        recovered += 1

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Total records: {len(df)}")
    print(f"Titles recovered from body: {recovered}")
    print()

    print("Job title source counts:")
    print(df["job_title_source"].value_counts(dropna=False).to_string())

    missing = (df["job_title_source"] == "MISSING").sum()
    present = len(df) - missing

    print()
    print(f"Titles present after body enrichment: {present}")
    print(f"Missing job titles: {missing}")
    print(f"Job title completeness: {present / len(df) * 100:.1f}%")
    print()
    print(f"Created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()