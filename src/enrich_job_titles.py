import csv
import re


INPUT_FILE = "data/processed/enriched_job_emails.csv"
OUTPUT_FILE = "data/processed/enriched_job_emails_with_titles.csv"


# --------------------------------------------------
# TITLE QUALITY
# --------------------------------------------------

SUSPICIOUS_EXACT = {
    "a",
    "an",
    "the",
    "following",
    "position",
    "role",
    "job",
    "opportunity",
    "career opportunities",
    "application",
    "your application",
    "this position",
    "this role",
    "helping us",
    "working",
}


SUSPICIOUS_FRAGMENTS = [
    "thank you for",
    "thanks for",
    "your interest",
    "our interest",
    "your application",
    "application has",
    "application was",
    "application received",
    "career opportunities",
    "click here",
    "http://",
    "https://",
    "and for your interest",
    "and are thrilled",
    "has been received",
]


def clean_title(title):
    if not title:
        return ""

    title = re.sub(r"\s+", " ", title).strip()

    title = title.strip(" -–—:|,.!\"'")

    return title


def is_valid_existing_title(title):
    title = clean_title(title)

    if not title:
        return False

    lower = title.lower()

    if lower in SUSPICIOUS_EXACT:
        return False

    if any(fragment in lower for fragment in SUSPICIOUS_FRAGMENTS):
        return False

    if len(title) <= 2:
        return False

    if len(title.split()) > 15:
        return False

    return True

def is_valid_extracted_title(title, company):
    title = clean_title(title)
    company = clean_title(company)

    if not title:
        return False

    lower = title.lower()

    bad_prefixes = (
        "to ",
        "at ",
        "with ",
        "for ",
    )

    if lower.startswith(bad_prefixes):
        return False

    bad_exact = {
        "confirmation",
        "next steps",
        "issue detected",
        "a job",
        "job",
    }

    if lower in bad_exact:
        return False

    # If extraction is simply the company name,
    # it is not a job title.
    if company and lower == company.lower():
        return False

    return is_valid_existing_title(title)

# --------------------------------------------------
# SUBJECT TITLE EXTRACTION
# --------------------------------------------------

def extract_title_from_subject(subject, company):
    subject = clean_title(subject)

    if not subject:
        return ""

    patterns = [

        # Application Received for <title>
        r"^application received for:?\s+(.+)$",

        # Application received: <title> – View your match score
        r"^application received:\s*(.+?)(?:\s+[–—-]\s+view your match score)?$",

        # Your interest in <title> at <company>
        r"^your interest in\s+(.+?)\s+at\s+.+$",

        # Thank you for applying to the <title> position
        r"^thank you for applying to the\s+(.+?)\s+position(?:\s+(?:at|with)\s+.+)?[.!]?$",

        # Thank you for applying to the <title> at <company>
        r"^thank you for applying to the\s+(.+?)\s+at\s+.+?[.!]?$",

        # Thank you for apply for <title> at <company>
        r"^thank you for apply for\s+(.+?)\s+at\s+.+?[.!]?$",

        # Company - Thank You For Applying to <title>
        r"^.+?\s+-\s+thank you for applying to\s+(.+)$",

        # Company - <title> Application Update
        r"^.+?\s+-\s+(.+?)\s+application update$",

        # IBM
        r"^you have successfully submitted your .+? job application\s+-\s+\S+\s+-\s+(.+)$",
    ]

    for pattern in patterns:
        match = re.match(
            pattern,
            subject,
            flags=re.IGNORECASE
        )

        if match:
            candidate = clean_title(match.group(1))

            if is_valid_extracted_title(candidate, company):
                return candidate

    return ""


# --------------------------------------------------
# SPECIAL HIGH-CONFIDENCE SUBJECT STRUCTURES
# --------------------------------------------------

def extract_special_subject_title(subject, company):
    subject = clean_title(subject)
    company = clean_title(company)

    lower = subject.lower()

    # --------------------------------------------------
    # American Express
    # Thank you for applying to <title>,
    # Enterprise Technology Services- <location> - <req>
    # --------------------------------------------------

    if company.lower() == "amex":

        match = re.match(
            r"^thank you for applying to\s+(.+?)\s*,\s*"
            r"enterprise technology services",
            subject,
            flags=re.IGNORECASE
        )

        if match:
            return clean_title(match.group(1))


    # --------------------------------------------------
    # UL Solutions
    # Your recent job application for <title> - <req>
    # --------------------------------------------------

    if company.lower() == "ul solutions":

        match = re.match(
            r"^your recent job application for\s+(.+?)\s+-\s+\d+\s*$",
            subject,
            flags=re.IGNORECASE
        )

        if match:
            return clean_title(match.group(1))


    # --------------------------------------------------
    # Jobgether
    # Next Steps for Your Job Application:
    # <title> at Jobgether
    # --------------------------------------------------

    if company.lower() == "jobgether":

        match = re.match(
            r"^next steps for your job application:\s*(.+?)\s+at\s+jobgether$",
            subject,
            flags=re.IGNORECASE
        )

        if match:
            return clean_title(match.group(1))


    # --------------------------------------------------
    # Schneider
    # Subject itself is the job title
    # --------------------------------------------------

    if company.lower() == "schneider":

        if re.search(
            r"\b(?:engineer|analyst|scientist|intern|developer)\b",
            subject,
            flags=re.IGNORECASE
        ):
            return clean_title(subject)


    # --------------------------------------------------
    # T-Mobile
    # Got it! Application received for:
    # REQ369271 Assoc Engineer, Software
    # --------------------------------------------------

    match = re.match(
        r"^got it!\s*application received for:\s*(.+)$",
        subject,
        flags=re.IGNORECASE
    )

    if match:
        candidate = clean_title(match.group(1))

        # Remove leading requisition number.
        candidate = re.sub(
            r"^REQ\d+\s+",
            "",
            candidate,
            flags=re.IGNORECASE
        )

        return clean_title(candidate)


    # --------------------------------------------------
    # DaVita
    # ... for Data Analyst ... |R0472175
    # --------------------------------------------------

    match = re.search(
        r'"\s*for\s+(.+?)\|R\d+\s*$',
        subject,
        flags=re.IGNORECASE
    )

    if match:
        return clean_title(match.group(1))


    # --------------------------------------------------
    # BNY
    # Thank You for Applying to BNY -
    # 81241 - <title> - Pittsburgh, PA
    # --------------------------------------------------

    if company.lower() == "bny":

        match = re.search(
            r"\bBNY\s*-\s*\d+\s*-\s*(.+?)\s*-\s*"
            r"[A-Za-z .'-]+,\s*[A-Z]{2}$",
            subject,
            flags=re.IGNORECASE
        )

        if match:
            return clean_title(match.group(1))


    # --------------------------------------------------
    # Fanatics
    # Thank you for applying to the
    # Quantitative Analyst I at Fanatics
    # --------------------------------------------------

    match = re.match(
        r"^thank you for applying to the\s+(.+?)\s+at\s+"
        + re.escape(company)
        + r"$",
        subject,
        flags=re.IGNORECASE
    )

    if company and match:
        return clean_title(match.group(1))


    # --------------------------------------------------
    # Horizon Media
    # Thank You for Applying to Horizon Media! <title>
    # --------------------------------------------------

    if company.lower() == "horizon media":
        match = re.match(
            r"^thank you for applying to horizon media!\s*(.+)$",
            subject,
            flags=re.IGNORECASE
        )

        if match:
            return clean_title(match.group(1))


    # --------------------------------------------------
    # CNA
    # Thank You for Applying! R-8129 - <title>
    # --------------------------------------------------

    if "cna" in company.lower():
        match = re.match(
            r"^thank you for applying!\s+R-\d+\s+-\s+(.+)$",
            subject,
            flags=re.IGNORECASE
        )

        if match:
            return clean_title(match.group(1))


    # --------------------------------------------------
    # Providence
    # Thank you for applying to <title> - <req>
    # --------------------------------------------------

    if company.lower() == "providence":
        match = re.match(
            r"^thank you for applying to\s+(.+?)\s+-\s+\d+\s*$",
            subject,
            flags=re.IGNORECASE
        )

        if match:
            return clean_title(match.group(1))


    # --------------------------------------------------
    # Ipsos
    # Thank you for applying to Ipsos – <title>
    # --------------------------------------------------

    if "ipsos" in company.lower():
        match = re.match(
            r"^thank you for applying to ipsos\s*[–—-]\s*(.+)$",
            subject,
            flags=re.IGNORECASE
        )

        if match:
            return clean_title(match.group(1))


    # --------------------------------------------------
    # Emory
    # Thank You for Applying to Our <title> Position!
    # --------------------------------------------------

    if company.lower() == "emory":
        match = re.match(
            r"^thank you for applying to our\s+(.+?)\s+position!?$",
            subject,
            flags=re.IGNORECASE
        )

        if match:
            return clean_title(match.group(1))


    # --------------------------------------------------
    # AB InBev
    # Thank you for applying to <title>
    # --------------------------------------------------

    if company.lower() == "ab inbev":
        match = re.match(
            r"^thank you for applying to\s+(.+)$",
            subject,
            flags=re.IGNORECASE
        )

        if match:
            candidate = clean_title(match.group(1))

            if is_valid_extracted_title(candidate, company):
                return candidate


    # --------------------------------------------------
    # ASM
    # Thank you for applying to ASM - <title>
    # --------------------------------------------------

    if company.lower() == "asm":
        match = re.match(
            r"^thank you for applying to asm\s+-\s+(.+)$",
            subject,
            flags=re.IGNORECASE
        )

        if match:
            return clean_title(match.group(1))


    # --------------------------------------------------
    # AST SpaceMobile
    # Thank you for applying to AST SpaceMobile for <title>
    # --------------------------------------------------

    if company.lower() == "ast spacemobile":
        match = re.match(
            r"^thank you for applying to ast spacemobile for\s+(.+)$",
            subject,
            flags=re.IGNORECASE
        )

        if match:
            return clean_title(match.group(1))


    # --------------------------------------------------
    # Gen
    # Thank you for applying at Gen- <title>
    # --------------------------------------------------

    if company.lower() == "gen":
        match = re.match(
            r"^thank you for applying at gen\s*-\s*(.+)$",
            subject,
            flags=re.IGNORECASE
        )

        if match:
            return clean_title(match.group(1))
        
    return ""

# --------------------------------------------------
# READ DATA
# --------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    records = list(reader)
    original_fieldnames = reader.fieldnames


# --------------------------------------------------
# ADD AUDIT COLUMNS
# --------------------------------------------------

fieldnames = list(original_fieldnames)

if "raw_job_title" not in fieldnames:
    fieldnames.append("raw_job_title")

if "job_title_source" not in fieldnames:
    fieldnames.append("job_title_source")


# --------------------------------------------------
# ENRICH TITLES
# --------------------------------------------------

source_counts = {
    "EXISTING": 0,
    "SUBJECT": 0,
    "MISSING": 0,
}

replaced_suspicious = 0


for record in records:

    raw_title = clean_title(record.get("job_title", ""))
    subject = record.get("subject", "")
    company = record.get("company_name", "")

    record["raw_job_title"] = raw_title


    # ----------------------------------------------
    # 1. Keep trustworthy existing title
    # ----------------------------------------------

    if is_valid_existing_title(raw_title):

        record["job_title"] = raw_title
        record["job_title_source"] = "EXISTING"

        source_counts["EXISTING"] += 1
        continue


    # Existing value was populated but untrustworthy.
    if raw_title:
        replaced_suspicious += 1


    # ----------------------------------------------
    # 2. Special subject structures
    # ----------------------------------------------

    title = extract_special_subject_title(
        subject,
        company
    )

    if title:

        record["job_title"] = title
        record["job_title_source"] = "SUBJECT"

        source_counts["SUBJECT"] += 1
        continue


    # ----------------------------------------------
    # 3. Generic subject structures
    # ----------------------------------------------

    title = extract_title_from_subject(
        subject,
        company
    )

    if title:

        record["job_title"] = title
        record["job_title_source"] = "SUBJECT"

        source_counts["SUBJECT"] += 1
        continue


    # ----------------------------------------------
    # 4. Leave unresolved
    # ----------------------------------------------

    record["job_title"] = ""
    record["job_title_source"] = "MISSING"

    source_counts["MISSING"] += 1


# --------------------------------------------------
# WRITE OUTPUT
# --------------------------------------------------

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as csv_file:

    writer = csv.DictWriter(
        csv_file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(records)


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

total = len(records)
titles_present = total - source_counts["MISSING"]

print(f"Total job-related emails: {total}")
print(f"Titles present after enrichment: {titles_present}")
print(f"Missing job titles: {source_counts['MISSING']}")

print(
    f"Job title completeness: "
    f"{titles_present / total * 100:.1f}%"
)

print(
    f"Suspicious existing titles replaced/removed: "
    f"{replaced_suspicious}"
)

print("\nJob title source counts:")

for source, count in source_counts.items():
    print(f"{source}: {count}")

print(f"\nCreated: {OUTPUT_FILE}")