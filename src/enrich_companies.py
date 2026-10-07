import csv
import re
from email.utils import parseaddr

from extract_gmail import (
    extract_company_name,
    extract_company_name_from_subject,
    extract_company_from_known_sender,
    extract_company_name_from_sender,
)


RAW_EMAIL_FILE = "data/raw/application_emails.csv"
RELEVANCE_FILE = "data/processed/final_email_relevance.csv"
OUTPUT_FILE = "data/processed/enriched_job_emails.csv"


# --------------------------------------------------
# CLEAN / VALIDATE COMPANY
# --------------------------------------------------

def clean_enriched_company(company):
    if not company:
        return None

    company = company.strip().strip('"').rstrip("!.,:;- ")

    # Remove common sender labels.
    suffix_patterns = [
        r"\s+Hiring Team$",
        r"\s+Talent Acquisition$",
        r"\s+Talent Team$",
        r"\s+Human Resources$",
        r"\s+People Services$",
        r"\s+Recruiting$",
        r"\s+Careers$",
        r"\s+Career Opportunities$",
        r"\s+No Reply$",
        r"\s+Workday Notifications?$",
        r"\s+Workday$",
        r"\s+HR$",
    ]

    for pattern in suffix_patterns:
        company = re.sub(
            pattern,
            "",
            company,
            flags=re.IGNORECASE
        ).strip()

    # Prefix cleanup.
    company = re.sub(
        r"^MyWorkday\s+",
        "",
        company,
        flags=re.IGNORECASE
    )

    company = re.sub(
        r"^Careers\s+",
        "",
        company,
        flags=re.IGNORECASE
    )

    company = re.sub(
        r"^noreply\s+",
        "",
        company,
        flags=re.IGNORECASE
    )

    company = re.sub(
        r"^do-not-reply\s+",
        "",
        company,
        flags=re.IGNORECASE
    )

    company = company.strip().rstrip("!.,:;- ")

    if not company:
        return None

    company_lower = company.lower()

    invalid_exact = {
        "workday",
        "workday workflow",
        "system administrator",
        "recruiting coordinator",
        "recruitment team",
        "talent acquisition team",
        "hiring team",
        "human resources",
        "hr",
        "no reply",
        "noreply",
        "that time",
    }

    if company_lower in invalid_exact:
        return None

    invalid_fragments = [
        "thank you for",
        "thanks for",
        "we've received",
        "we’ve received",
        "after reviewing resumes",
        "applicants whose skills",
        "position has been successfully closed",
        "http://",
        "https://",
    ]

    if any(
        fragment in company_lower
        for fragment in invalid_fragments
    ):
        return None

    # Long prose is almost certainly not a company.
    if len(company.split()) > 10:
        return None

    return company


# --------------------------------------------------
# COMPANY FROM SUBJECT
# --------------------------------------------------

def company_from_subject(subject):
    subject = subject.strip()

    patterns = [
        r"^we(?:'|’)ve received your (.+?) application!?$",
        r"^(.+?) software application$",
        r"^thanks from (.+?)!?$",
        r"^(.+?):\s*.+$",
        r"^thank you for appl(?:y|ying) for .+? at (.+?)(?:!|$)",
        r"^thank you for applying to .+? at (.+?)(?:!|$)",
        r"^(.+?)\s*-\s*thank you for applying",
        r"^thank you for applying at (.+?)(?:,\s*Dakshesh)?!?$",
        r"^thank you for applying to (.+?)(?:!|$)",
        r"^Dakshesh,\s*thank you for applying to (.+?)(?:!|$)",
        r"^thanks for your interest in (.+?)(?:!|$)",
        r"^thank you .*? for your interest in (.+?)(?:!|$)",
        r"^information about your application to (.+)$",
        r"^we(?:'|’)ve received your application for .+? at (.+)$",
        r"^thank you for your application to (.+?)(?:!|$)",
        r"^thank you for applying - (.+)$",
        r"^thank you for applying - (.+?) - .+$",
        r"^(.+?) application update\b",
        r"^employment update\s*-\s*(.+)$",
        r"^(.+?)\s*:\s*thank you for applying",
        r"^(.+?)\s*-\s*application received",
        r"^(.+?) application received",
        r"^(.+?)\s*-\s*we have received your application",
        r"^confirming your (.+?) job application$",
        r"^thank you for applying for a job at (.+)$",
        r"^your interest in .+? at (.+)$",
        r"^application received by (.+)$",
        r"^update on your application for .+? at (.+)$",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            subject,
            flags=re.IGNORECASE
        )

        if match:
            company = clean_enriched_company(
                match.group(1)
            )

            if company:
                return company

    return None


# --------------------------------------------------
# COMPANY FROM SENDER DISPLAY NAME
# --------------------------------------------------

def company_from_sender_display(sender):
    company = extract_company_name_from_sender(sender)

    if not company:
        return None

    # "Dani from DaVita Kidney Care"
    match = re.match(
        r"^.+?\s+from\s+(.+)$",
        company,
        flags=re.IGNORECASE
    )

    if match:
        company = match.group(1)

    # "Workday at DMA"
    match = re.match(
        r"^Workday\s+at\s+(.+)$",
        company,
        flags=re.IGNORECASE
    )

    if match:
        company = match.group(1)

    # "Workday @ Intel Notification"
    match = re.match(
        r"^Workday\s*@\s*(.+?)(?:\s+Notification)?$",
        company,
        flags=re.IGNORECASE
    )

    if match:
        company = match.group(1)

    # "DoNotReply-WorkdayNotifications RTX"
    match = re.match(
        r"^DoNotReply-WorkdayNotifications\s+(.+)$",
        company,
        flags=re.IGNORECASE
    )

    if match:
        company = match.group(1)

    return clean_enriched_company(company)


# --------------------------------------------------
# COMPANY FROM EMPLOYER-SPECIFIC EMAIL ADDRESS
# --------------------------------------------------

def company_from_sender_address(sender):
    _, email_address = parseaddr(sender)

    if not email_address:
        # Handles senders stored as just an address.
        email_address = sender.strip()

    if "@" not in email_address:
        return None

    local_part, domain = email_address.split("@", 1)

    domain = domain.lower()

    # Shared ATS domains should not be interpreted as employers.
    shared_domains = {
        "myworkday.com",
        "us.greenhouse-mail.io",
        "greenhouse-mail.io",
        "mail.paylocity.com",
        "app.bamboohr.com",
        "talent.icims.com",
        "smartrecruiters.com",
        "ashbyhq.com",
        "hire.lever.co",
        "ultipro.com",
        "saashr.com",
        "dayforce.com",
        "avature.net",
        "governmentjobs.com",
        "brassring.com",
    }

    # Workday is special: employer is often encoded in local part.
    if domain == "myworkday.com":
        generic_local_parts = {
            "workday",
            "globalhr",
            "notification",
            "notifications",
        }

        if local_part in generic_local_parts:
            return None

        return clean_enriched_company(
            local_part.replace(".", " ").replace("_", " ")
        )

    # Other shared ATS domains cannot safely identify employer.
    if domain == "ultipro.com":

        cleaned_local = re.sub(
            r"^(?:no[_-]?reply|noreply)",
            "",
            local_part,
            flags=re.IGNORECASE
        )

        cleaned_local = cleaned_local.strip("_- ")

        if cleaned_local:
            # CamelCase:
            # RanchEhrloSociety -> Ranch Ehrlo Society
            cleaned_local = re.sub(
                r"(?<=[a-z])(?=[A-Z])",
                " ",
                cleaned_local
            )

            return clean_enriched_company(
                cleaned_local
            )
    
    if domain in shared_domains:
        return None

    domain_company_map = {
        "pella.com": "Pella",
        "viavisolutions.com": "VIAVI Solutions",
        "noom.com": "Noom",
        "onestream.com": "OneStream",
    }

    if domain in domain_company_map:
        return domain_company_map[domain]

    return None


# --------------------------------------------------
# LOAD VALID JOB-RELATED EMAIL IDS
# --------------------------------------------------

job_email_ids = set()

with open(RELEVANCE_FILE, "r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)

    for record in reader:
        if record["final_relevance"] == "JOB_RELATED":
            job_email_ids.add(record["email_id"])


# --------------------------------------------------
# ENRICH JOB EMAILS
# --------------------------------------------------

records = []

with open(RAW_EMAIL_FILE, "r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)

    for record in reader:

        if record["email_id"] not in job_email_ids:
            continue

        existing_company = clean_enriched_company(
            record["company_name"]
        )

        subject_company = company_from_subject(
            record["subject"]
        )

        known_sender_company = clean_enriched_company(
            extract_company_from_known_sender(
                record["sender"]
            )
        )

        sender_display_company = company_from_sender_display(
            record["sender"]
        )

        sender_address_company = company_from_sender_address(
            record["sender"]
        )

        body_company = clean_enriched_company(
            extract_company_name(
                record["email_body"]
            )
        )

        # Confidence hierarchy.
        if existing_company:
            company = existing_company
            company_source = "EXISTING"

        elif subject_company:
            company = subject_company
            company_source = "SUBJECT"

        elif known_sender_company:
            company = known_sender_company
            company_source = "KNOWN_SENDER"

        elif sender_display_company:
            company = sender_display_company
            company_source = "SENDER_DISPLAY"

        elif sender_address_company:
            company = sender_address_company
            company_source = "SENDER_ADDRESS"

        elif body_company:
            company = body_company
            company_source = "BODY"

        else:
            company = ""
            company_source = "MISSING"

        enriched_record = dict(record)

        # Preserve original raw extraction.
        enriched_record["raw_company_name"] = record["company_name"]

        # Analysis-ready company.
        enriched_record["company_name"] = company
        enriched_record["company_source"] = company_source

        records.append(enriched_record)


# --------------------------------------------------
# SAVE ENRICHED DATA
# --------------------------------------------------

fieldnames = list(records[0].keys())

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
# QUALITY SUMMARY
# --------------------------------------------------

missing = [
    record
    for record in records
    if not record["company_name"]
]

source_counts = {}

for record in records:
    source = record["company_source"]

    source_counts[source] = (
        source_counts.get(source, 0) + 1
    )


print(f"Total job-related emails: {len(records)}")
print(f"Missing company names: {len(missing)}")
print(
    f"Company completeness: "
    f"{((len(records) - len(missing)) / len(records)) * 100:.1f}%"
)

print("\nCompany source counts:")

for source, count in source_counts.items():
    print(f"{source}: {count}")


print("\n=== STILL MISSING COMPANIES ===")

for record in missing:
    print("\n----------------------------------------")
    print("Email ID:", record["email_id"])
    print("Subject:", record["subject"])
    print("Sender:", record["sender"])


print(f"\nCreated: {OUTPUT_FILE}")