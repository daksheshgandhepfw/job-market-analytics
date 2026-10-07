from bs4 import BeautifulSoup
import os
import re
import csv
import base64
import time
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def authenticate_gmail():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)

    return service

def execute_with_retry(request, max_retries=5):
    """
    Execute a Gmail API request and retry temporary
    rate-limit errors using exponential backoff.
    """

    for attempt in range(max_retries):
        try:
            return request.execute()

        except HttpError as error:
            status = error.resp.status

            if status in (403, 429):
                wait_seconds = 2 ** attempt

                print(
                    f"Gmail API rate limit reached. "
                    f"Waiting {wait_seconds} seconds..."
                )

                time.sleep(wait_seconds)
                continue

            raise

    raise RuntimeError(
        "Gmail API request failed after multiple retries."
    )

def find_application_emails(service):
    query = '"thank you for applying"'

    messages = []
    page_token = None

    while True:
        request = (
            service.users()
            .messages()
            .list(
                userId="me",
                q=query,
                maxResults=100,
                pageToken=page_token
            )
        )

        results = execute_with_retry(request)

        messages.extend(
            results.get("messages", [])
        )

        page_token = results.get("nextPageToken")

        if not page_token:
            break

    return messages

def get_email(service, message_id):
    """
    Retrieve one Gmail message and extract both
    metadata and body from a single API request.
    """

    request = (
        service.users()
        .messages()
        .get(
            userId="me",
            id=message_id,
            format="full"
        )
    )

    message = execute_with_retry(request)

    payload = message["payload"]
    headers = payload.get("headers", [])

    metadata = {
        "email_id": message_id,
        "subject": "",
        "sender": "",
        "date": ""
    }

    # Extract metadata from the full message
    for header in headers:
        if header["name"] == "Subject":
            metadata["subject"] = header["value"]

        elif header["name"] == "From":
            metadata["sender"] = header["value"]

        elif header["name"] == "Date":
            metadata["date"] = header["value"]

    # Extract body
    body = ""

    if "parts" in payload:
        body = extract_text_from_parts(payload["parts"])

    if not body:
        body_data = payload.get("body", {}).get("data")

        if body_data:
            body = base64.urlsafe_b64decode(
                body_data
            ).decode(
                "utf-8",
                errors="ignore"
            )

    return metadata, body

def extract_text_from_parts(parts):
    html_body = ""

    for part in parts:
        mime_type = part["mimeType"]

        if mime_type == "text/plain":
            body_data = part.get("body", {}).get("data")

            if body_data:
                return base64.urlsafe_b64decode(body_data).decode(
                    "utf-8",
                    errors="ignore"
                )

        elif mime_type == "text/html":
            body_data = part.get("body", {}).get("data")

            if body_data:
                html_body = base64.urlsafe_b64decode(body_data).decode(
                    "utf-8",
                    errors="ignore"
                )

        if "parts" in part:
            text = extract_text_from_parts(part["parts"])

            if text:
                return text

    return html_body


def clean_email_body(body):
    soup = BeautifulSoup(body, "html.parser")

    text = soup.get_text(separator=" ", strip=True)

    text = " ".join(text.split())

    return text


def normalize_job_title(job_title, company_name=None):
    """
    Clean framing text from an extracted job title without
    changing the actual title.
    """

    if not job_title:
        return None

    job_title = " ".join(job_title.split()).strip()

    # Remove common leading framing words
    leading_patterns = [
        r"^the role of\s+",
        r"^the\s+",
        r"^open\s+",
    ]

    for pattern in leading_patterns:
        job_title = re.sub(
            pattern,
            "",
            job_title,
            flags=re.IGNORECASE
        )

    # Remove reference IDs when they are attached as metadata
    job_title = re.sub(
        r"\s*\(ID:\s*\d+\)\s*$",
        "",
        job_title,
        flags=re.IGNORECASE
    )

    job_title = re.sub(
        r"\s*\(RQ\d+\)\s*$",
        "",
        job_title,
        flags=re.IGNORECASE
    )

    # Remove common trailing framing words
    job_title = re.sub(
        r"\s+position$",
        "",
        job_title,
        flags=re.IGNORECASE
    )

    job_title = re.sub(
        r"\s+role$",
        "",
        job_title,
        flags=re.IGNORECASE
    )

    # Remove company framing when we already know the company
    if company_name:
        escaped_company = re.escape(company_name)

        job_title = re.sub(
            rf"\s+position\s+at\s+{escaped_company}$",
            "",
            job_title,
            flags=re.IGNORECASE
        )

        job_title = re.sub(
            rf"\s+role\s+(?:at|with us here at)\s+{escaped_company}$",
            "",
            job_title,
            flags=re.IGNORECASE
        )

        job_title = re.sub(
            rf"\s+at\s+{escaped_company}$",
            "",
            job_title,
            flags=re.IGNORECASE
        )

    return job_title.strip(" !.,-")


def is_valid_job_title(job_title):
    """
    Reject obvious sentence fragments and generic phrases that
    are not actual job titles.
    """

    if not job_title:
        return False

    title_lower = job_title.lower().strip()

    invalid_phrases = [
        "future openings",
        "appreciate your continued engagement",
        "a career",
        "joining our team",
        "joining the team",
        "advancing our mission",
        "we appreciate",
        "we regret",
        "your application is important",
        "your background and experience",
        "your qualifications",
        "our recruitment team",
    ]

    if any(
        phrase in title_lower
        for phrase in invalid_phrases
    ):
        return False

    # Very long results are usually sentence overcaptures,
    # not job titles.
    if len(job_title.split()) > 18:
        return False

    return True


def extract_job_title(body, company_name=None):
    """
    Extract a job title from the email body.

    More specific patterns are checked before broader patterns.
    Invalid candidates are skipped rather than forced.
    """

    patterns = [
        # Thank you for applying for the role of X
        r"thank you for applying for the role of ([^.!]+)",

        # Thank you / Thanks for applying for X
        r"(?:thank you|thanks(?: so much)?) for applying for ([^.!]+)",

        # Expressing interest in the Company + Title position
        r"expressing interest in the [^.!]*? ([A-Z][^.!]+?) position",

        # Received your application for X position
        r"received your application for the ([^.!]+?) position",

        # Mass General / RQ-style
        r"interest in the (.*?) \(RQ\d+\) position",

        # Amazon / ID-style
        r"received your application for the (.*?) \(ID:\s*\d+\) position",

        # Position explicitly labelled
        r"\*?Position:\*?\s*(.*?)\s+Thank you",

        # Position of X
        r"application for the position of ([^.!]+)",

        # Application successfully submitted
        r"application for ([^.!]+?) was successfully submitted",

        # Application received
        r"application to the ([^.!]+?) position has been received",

        # Applying to job-reference + title
        r"applying to J\d+\s+([^.]+)",

        # Applying to our X position
        r"applying to our (?!position\b)([^.!]+?) position",

        # Applying to the X position
        r"applying to the ([^.!]+?) position",

        # Applying for the X position
        r"applying for the ([^.!]+?) position",

        # Apply for the X position
        r"apply for the ([^.!]+?) position",

        # Applying for X role
        r"applying for the ([^.!]+?) role",

        # Apply for X role at...
        r"apply for the ([^.!]+?) role at",

        # Applying to X for the Y position
        r"applying to [^.!]+? for the ([^.!]+?) position",

        # Rejection wording
        r"not move forward with your application for ([^.!]+?) at this time",

        # Interest wording — lower confidence, so checked last
        r"your interest in ([^.!]+?) with ",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            body,
            re.IGNORECASE
        )

        if not match:
            continue

        candidate = match.group(1).strip()

        # If the candidate begins with the known company name,
        # remove the company prefix.
        if company_name:
            company_prefix = company_name + " "

            if candidate.lower().startswith(
                company_prefix.lower()
            ):
                candidate = candidate[
                    len(company_prefix):
                ].strip()

        # Reject obvious sentence fragments / bad candidates.
        if not is_valid_job_title(candidate):
            continue

        # Remove framing such as "the", "position", "role at Company", etc.
        candidate = normalize_job_title(
            candidate,
            company_name
        )

        # Validate again after normalization.
        if is_valid_job_title(candidate):
            return candidate

    return None


def extract_job_title_from_subject(subject, company_name=None):
    """
    Use the subject as a fallback when the body does not provide
    a reliable job title.
    """

    patterns = [
        # Your Application for X at Company
        r"^your application for (.+?) at .+$",

        # Invenergy Job Application for X
        r"^.+? job application for (.+)$",

        # Filled-position notification
        r"^thank you for applying,\s*the (.+?) position has been filled$",

        # Workday-style: R123456 Job Title role
        r"^thank you for applying!\s*\|\s*R\d+\s+(.+?)\s+role$",

        # CATHEXIS-style
        r"^(.+?\(req-\d+\))\s*-\s*.+$",

        # Iambic-style
        r"^thank you for applying for the (.+?) at .+$",

        # Application confirmation for R123456 Title
        r"^application confirmation for R\d+\s+(.+)$",

        # Jabil subject
        r"^thank you for your recent application with Jabil\s+J\d+\s+(.+)$",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            subject,
            re.IGNORECASE
        )

        if not match:
            continue

        candidate = match.group(1).strip()

        if not is_valid_job_title(candidate):
            continue

        candidate = normalize_job_title(
            candidate,
            company_name
        )

        if is_valid_job_title(candidate):
            return candidate

    return None

def clean_company_name(company_name):
    if not company_name:
        return None

    company_name = company_name.strip().strip('"')

    # Remove personalized endings
    company_name = re.sub(
        r",?\s*Dakshesh!?$",
        "",
        company_name,
        flags=re.IGNORECASE
    )

    # Remove common recruiting/ATS labels from the end
    company_name = re.sub(
        r"\s+Hiring Team$",
        "",
        company_name,
        flags=re.IGNORECASE
    )

    company_name = re.sub(
        r"\s+Talent Acquisition$",
        "",
        company_name,
        flags=re.IGNORECASE
    )

    company_name = re.sub(
        r"\s+Recruiting$",
        "",
        company_name,
        flags=re.IGNORECASE
    )

    company_name = re.sub(
        r"\s+Careers$",
        "",
        company_name,
        flags=re.IGNORECASE
    )

    company_name = re.sub(
        r"\s+People Services$",
        "",
        company_name,
        flags=re.IGNORECASE
    )

    company_name = re.sub(
        r"\s+Workday Notifications?$",
        "",
        company_name,
        flags=re.IGNORECASE
    )

    company_name = re.sub(
        r"\s+Workday$",
        "",
        company_name,
        flags=re.IGNORECASE
    )

    # iCIMS display names often look like:
    # "Canon Careers @ icims"
    company_name = re.sub(
        r"\s*@\s*icims$",
        "",
        company_name,
        flags=re.IGNORECASE
    )

    company_name = company_name.rstrip("!.,:;- ")

    if not company_name:
        return None

    invalid_names = {
        "our team",
        "workday",
        "workday notification",
        "workday workflow",
        "system administrator",
        "recruiting coordinator",
        "recruitment team",
        "talent acquisition team",
        "hiring team",
        "careers",
        "candidate support",
        "human resources",
        "hr",
        "no reply",
        "noreply",
        "do not reply"
    }
    
    invalid_fragments = [
        "thank you for",
        "thanks for",
        "we've received",
        "we’ve received",
        "update on your",
        "dakshesh,",
        "confirming your",
        "we are reviewing your",
        "application received",
        "application submitted",
        "application status",
        "workday notification",
        "workday workflow",
        "hr inbox"
    ]

    company_lower = company_name.lower()

    if any(
        fragment in company_lower
        for fragment in invalid_fragments
    ):
        return None

    if company_name.lower() in invalid_names:
        return None

    if company_name.lower().startswith(
        ("http://", "https://", "www.")
    ):
        return None

    if "http://" in company_name.lower():
        return None

    if "https://" in company_name.lower():
        return None

    return company_name


def extract_company_name(body):
    patterns = [
        r"thank you for applying to ([^.!]+?) for the",
        r"thank you for your interest in a career with ([^.!]+)[.!]",
        r"thank you for your interest in ([^.!]+)!",
        r"applying for .*? at (.*?)[.!]",
        r"applying with (.*?)!",
        r"joining (.*?) and the time",
        r"role at ([^.!]+)[.!]",
        r"application to (.*?) has been received",
        r"Regards,\s*The (.*?) Team",
        r"interest in .*? with (.*?)(?:\. Unfortunately| Unfortunately)"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            body,
            re.IGNORECASE
        )

        if match:
            company_name = clean_company_name(
                match.group(1)
            )

            if company_name:
                return company_name

    return None


def extract_company_name_from_subject(subject):
    job_reference_id = extract_job_reference_id(subject)

    if (
        job_reference_id
        and job_reference_id.upper().startswith("RQ")
    ):
        return None

    patterns = [
        # Thank-you patterns
        r"^(.+?)\s*-\s*thank you for applying!?$",
        r"^thank you for applying at (.+?)(?:,\s*Dakshesh)?!?$",
        r"^thank you for applying to (.+?)(?:!|$)",
        r"^thank you for applying with (.+?)!?$",

        # Application/update patterns
        r"^update on your application with (.+)$",
        r"^important information about your application to (.+)$",
        r"^information about your application to (.+)$",
        r"^(.+?) application:\s*status update$",
        r"^(.+?) application update(?:\s*-\s*.+)?$",

        # Interest patterns
        r"^thank you for your interest in (.+?)!?$",
        r"^thanks for your interest in (.+?)!?$",
        r"^we appreciate your interest in (.+?)!?$",

        # Explicit "at COMPANY"
        r"^your application for .+ at (.+)$",
        r"^we(?:'|’)ve received your application for .+ at (.+)$",

        # Other useful company-bearing formats
        r"^(.+?)\s*-\s*thank you for applying to .+$",
        r"^(.+?):\s*thank you for applying.*$",

        # Existing pattern
        r"^candidate privacy policy notification from (.+)$"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            subject.strip(),
            re.IGNORECASE
        )

        if match:
            company_name = clean_company_name(
                match.group(1)
            )

            if company_name:
                return company_name

    return None


def extract_company_from_known_sender(sender):
    sender_lower = sender.lower()

    sender_company_map = {
        "careers@jovianconcepts.com": "Jovian Concepts",
        "bakerhughes@myworkday.com": "Baker Hughes",
        "workday@bah.com": "Booz Allen Hamilton"
    }

    for sender_pattern, company_name in sender_company_map.items():
        if sender_pattern in sender_lower:
            return company_name

    return None


def extract_company_name_from_sender(sender):
    # Extract display name:
    # "Philips People Services <philips@myworkday.com>"
    # -> Philips People Services

    match = re.match(
        r'^\s*"?(.+?)"?\s*<[^>]+>\s*$',
        sender
    )

    if not match:
        return None

    display_name = match.group(1).strip().strip('"')

    company_name = clean_company_name(
        display_name
    )

    return company_name

def print_email_structure(parts, level=0):
    for part in parts:
        print("  " * level + part["mimeType"])

        if "parts" in part:
            print_email_structure(part["parts"], level + 1)

def classify_email(body, subject=""):
    """
    Classify a job-related email using both
    the subject line and email body.
    """

    body_lower = body.lower()
    subject_lower = subject.lower()

    text_lower = f"{subject_lower} {body_lower}"

    # --------------------------------------------------
    # 1. CONDITIONAL / FUTURE REJECTION LANGUAGE
    # --------------------------------------------------

    # These phrases may describe what could happen later,
    # rather than an actual rejection decision.

    conditional_rejection_phrases = [
        "if you are not selected",
        "if you're not selected",
        "if you’re not selected",
        "if you haven't heard",
        "if you haven’t heard"
    ]

    has_conditional_rejection_language = any(
        phrase in text_lower
        for phrase in conditional_rejection_phrases
    )

    # --------------------------------------------------
    # 2. STRONG REJECTION SIGNALS
    # --------------------------------------------------

    strong_rejection_phrases = [
        "will not be moving ahead",
        "will not be moving forward",
        "not be moving forward",
        "decided not to move forward",
        "decided to not move forward",
        "decision to not move forward",
        "decided to pursue another candidate",
        "unable to proceed with your application",
        "identified candidates whose skills and backgrounds more closely match",
        "this position has been filled",
        "decided to move forward with candidates whose qualification",
        "decided not to proceed further with your candidacy",
        "decided not to proceed with your candidacy",
        "not been selected as the best match"
    ]

    for phrase in strong_rejection_phrases:
        if phrase in text_lower:
            return "Rejection"

    # --------------------------------------------------
    # 3. WEAK REJECTION SIGNALS
    # --------------------------------------------------

    weak_rejection_phrases = [
        "not selected",
        "not been selected",
        "other candidates"
    ]

    if not has_conditional_rejection_language:
        for phrase in weak_rejection_phrases:
            if phrase in text_lower:
                return "Rejection"

    # --------------------------------------------------
    # 4. STRONG APPLICATION CONFIRMATION SIGNALS
    # --------------------------------------------------

    confirmation_phrases = [
        "we've received your application",
        "we have received your application",
        "we just received your application",
        "we received your application",
        "application has been received",
        "received your application for",
        "application was successfully submitted",
        "application has been successfully submitted",
        "application submission confirmation",
        "application is now with our talent acquisition team",
        "application has been received and is currently under review"
    ]

    for phrase in confirmation_phrases:
        if phrase in text_lower:
            return "Application Confirmation"

    # --------------------------------------------------
    # 5. GENERAL APPLICATION CONFIRMATION SIGNALS
    # --------------------------------------------------

    if (
        ("thank you" in text_lower or "thanks" in text_lower)
        and "applying" in text_lower
    ):
        return "Application Confirmation"

    if (
        ("thank you" in text_lower or "thanks" in text_lower)
        and "your application" in text_lower
    ):
        return "Application Confirmation"

    if (
        "application" in text_lower
        and "received" in text_lower
    ):
        return "Application Confirmation"

    if (
        "application" in text_lower
        and "submitted" in text_lower
    ):
        return "Application Confirmation"

    # --------------------------------------------------
    # 6. OTHER
    # --------------------------------------------------

    return "Other"

def extract_job_reference_id(body):
    patterns = [
        r"\(ID:\s*(\d+)\)",
        r"\b(RQ\d+)\b",
        r"\b(J\d+)\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, body, re.IGNORECASE)

        if match:
            return match.group(1).strip()

    return None

if __name__ == "__main__":
    service = authenticate_gmail()

    output_file = "data/raw/application_emails.csv"

    fieldnames = [
        "email_id",
        "email_date",
        "sender",
        "subject",
        "email_body",
        "company_name",
        "job_title",
        "job_reference_id",
        "email_type"
    ]

    # --------------------------------------------------
    # LOAD EMAILS WE ALREADY EXTRACTED
    # --------------------------------------------------

    existing_records = []
    existing_email_ids = set()

    try:
        with open(
            output_file,
            "r",
            encoding="utf-8"
        ) as csv_file:

            reader = csv.DictReader(csv_file)
            existing_records = list(reader)

            existing_email_ids = {
                record["email_id"]
                for record in existing_records
            }

    except FileNotFoundError:
        # First-ever extraction: there is no existing CSV yet.
        pass

    print(
        f"Already saved emails: {len(existing_email_ids)}"
    )

    # --------------------------------------------------
    # SEARCH GMAIL
    # --------------------------------------------------

    messages = find_application_emails(service)

    print(
        f"Emails matching Gmail search: {len(messages)}"
    )

    # Only process emails we have never extracted before.
    new_messages = [
        message
        for message in messages
        if message["id"] not in existing_email_ids
    ]

    print(
        f"New emails to process: {len(new_messages)}"
    )

    # --------------------------------------------------
    # PROCESS ONLY NEW EMAILS
    # --------------------------------------------------

    for number, message in enumerate(new_messages, start=1):

        print(
            f"Processing new email "
            f"{number}/{len(new_messages)}"
        )

        # One Gmail API request gives us both metadata and body.
        metadata, body = get_email(
            service,
            message["id"]
        )

        clean_body = clean_email_body(body)

        # --------------------------------------------------
        # EXTRACT COMPANY NAME
        # --------------------------------------------------

        # Try body first.
        company_name = extract_company_name(
            clean_body
        )

        # Then try subject.
        if company_name is None:
            company_name = extract_company_name_from_subject(
                metadata["subject"]
            )

        # Controlled sender fallback.
        if company_name is None:
            sender_company = extract_company_name_from_sender(
                metadata["sender"]
            )

            if sender_company == "Mass General Brigham":
                company_name = sender_company

            elif "alphaomegaintegration" in metadata["sender"].lower():
                company_name = "Alpha Omega"

        # Try subject again if still missing.
        if not company_name:
            company_name = extract_company_name_from_subject(
                metadata["subject"]
            )

        # Known-sender fallback.
        if not company_name:
            company_name = extract_company_from_known_sender(
                metadata["sender"]
            )

        # --------------------------------------------------
        # CLASSIFY EMAIL
        # --------------------------------------------------

        email_type = classify_email(
            clean_body,
            metadata["subject"]
        )

        # --------------------------------------------------
        # EXTRACT JOB TITLE
        # --------------------------------------------------

        job_title = extract_job_title(
            clean_body,
            company_name
        )

        # Subject fallback.
        if job_title is None:
            job_title = extract_job_title_from_subject(
                metadata["subject"],
                company_name
            )

        # --------------------------------------------------
        # EXTRACT JOB REFERENCE ID
        # --------------------------------------------------

        job_reference_id = extract_job_reference_id(
            clean_body
        )

        # --------------------------------------------------
        # CREATE EMAIL RECORD
        # --------------------------------------------------

        new_record = {
            "email_id": metadata["email_id"],
            "email_date": metadata["date"],
            "sender": metadata["sender"],
            "subject": metadata["subject"],
            "email_body": clean_body,
            "company_name": company_name,
            "job_title": job_title,
            "job_reference_id": job_reference_id,
            "email_type": email_type
        }

        # --------------------------------------------------
        # CHECKPOINT: SAVE EACH EMAIL IMMEDIATELY
        # --------------------------------------------------

        with open(
            output_file,
            "a",
            newline="",
            encoding="utf-8"
        ) as csv_file:

            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames
            )

            writer.writerow(new_record)

    # --------------------------------------------------
    # EXTRACTION SUMMARY
    # --------------------------------------------------

    print("\nExtraction complete.")
    print(
        f"Previously saved emails: {len(existing_records)}"
    )
    print(
        f"New emails processed: {len(new_messages)}"
    )
    print(
        f"Total saved emails: "
        f"{len(existing_records) + len(new_messages)}"
    )
    print(
        f"Saved to {output_file}"
    )