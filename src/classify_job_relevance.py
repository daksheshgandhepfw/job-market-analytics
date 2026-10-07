import csv


INPUT_FILE = "data/raw/application_emails.csv"
OUTPUT_FILE = "data/processed/email_relevance.csv"


def classify_relevance(record):

    subject = record["subject"].lower()
    sender = record["sender"].lower()

    # --------------------------------------------------
    # CLEAR NON-JOB EDUCATION / ADMISSIONS SENDERS
    # --------------------------------------------------

    education_sender_terms = [
        "uwindsor.ca",
        "uwaterloo.ca",
        "gradadmissions.pitt.edu",
        "sciadmit@pitt.edu",
        "gseasadmission@virginia.edu",
        "admissions.msu.edu",
        "admissionraisoni@raisoni.net"
    ]

    for term in education_sender_terms:
        if term in sender:
            return "NOT_JOB_RELATED"

    # --------------------------------------------------
    # CLEAR NON-APPLICATION SUBJECTS
    # --------------------------------------------------

    non_job_subject_terms = [
        "applicant webinar",
        "all builders welcome grant",
        "volunteer program",
        "international applicant webinar",
        "workday inbox - your daily digest",
        "talent community",
        "activate your university",
        "degree program"
    ]

    for term in non_job_subject_terms:
        if term in subject:
            return "NOT_JOB_RELATED"

    # --------------------------------------------------
    # STRONG JOB-RELATED SIGNALS
    # --------------------------------------------------

    job_sender_terms = [
        # Major ATS / recruiting platforms
        # Additional ATS / recruiting platforms
        "ultipro.com",
        "bamboohr.com",
        "applytojob.com",
        "dayforce.com",
        "adp.com",
        "gem.com",
        "governmentjobs.com",
        "newtonsoftware.com",
        "saashr.com",
        "candidatecare.com",
        "brassring.com",

        # Recruiting-specific sender patterns
        "recruitment-no-reply",
        "recruiting-noreply",
        "talentacquisition",
        "talent@",
        "jobs@",
        "greenhouse-mail.io",
        "ashbyhq.com",
        "myworkday.com",
        "workday.",
        "smartrecruiters.com",
        "hire.lever.co",
        "talent.icims.com",
        "workablemail.com",
        "notifications.ukg.net",
        "mail.paylocity.com",
        "ats.rippling.com",
        "avature.net",
        "oraclecloud.com",
        "comeet-notifications.com",

        # Employment / recruiting domains
        "amazon.jobs",
        "spacex.com",
        "recruitment.americanexpress.com",
        "jobs@ixl.com",
        "ta.smxtech.com",
        "onestream.com",
        "getgarner.com",
        "send.applicantemails.com",
        "talentacquisition.abbvie.com",
        "howmet.com",
        "careers.intusurg.com",
        "talentconnect@crown.com",
        "talentacquisition@monsterenergy.com",

        # Employer-specific recruiting systems
        "ultalentacquisition",
        "workday.notifications",
        "hrss_automated_message",
        "recruitingcoordinator",
        "recruiting@",
        "careers@"
    ]

    for term in job_sender_terms:
        if term in sender:
            return "JOB_RELATED"

    # --------------------------------------------------
    # EVERYTHING ELSE REQUIRES REVIEW
    # --------------------------------------------------

    return "REVIEW"


with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as csv_file:

    reader = csv.DictReader(csv_file)
    records = list(reader)


results = []


for record in records:

    relevance = classify_relevance(record)

    results.append(
        {
            "email_id": record["email_id"],
            "subject": record["subject"],
            "sender": record["sender"],
            "email_type": record["email_type"],
            "email_relevance": relevance
        }
    )


with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as csv_file:

    fieldnames = [
        "email_id",
        "subject",
        "sender",
        "email_type",
        "email_relevance"
    ]

    writer = csv.DictWriter(
        csv_file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(results)


job_related = sum(
    record["email_relevance"] == "JOB_RELATED"
    for record in results
)

not_job_related = sum(
    record["email_relevance"] == "NOT_JOB_RELATED"
    for record in results
)

review = sum(
    record["email_relevance"] == "REVIEW"
    for record in results
)


print("=== JOB RELEVANCE CLASSIFICATION ===")
print("Total emails:", len(results))
print("JOB_RELATED:", job_related)
print("NOT_JOB_RELATED:", not_job_related)
print("REVIEW:", review)

print(
    "\nSaved:",
    OUTPUT_FILE
)

from collections import Counter


review_records = [
    record
    for record in results
    if record["email_relevance"] == "REVIEW"
]


print("\n=== REVIEW EMAIL ANALYSIS ===")


# --------------------------------------------------
# MOST COMMON SENDERS
# --------------------------------------------------

review_sender_counts = Counter(
    record["sender"]
    for record in review_records
)


print("\n=== REVIEW: MOST COMMON SENDERS ===")

for sender, count in review_sender_counts.most_common(40):
    print(
        f"{count:>3} | {sender}"
    )


# --------------------------------------------------
# MOST COMMON SUBJECTS
# --------------------------------------------------

review_subject_counts = Counter(
    record["subject"]
    for record in review_records
)


print("\n=== REVIEW: MOST COMMON SUBJECTS ===")

for subject, count in review_subject_counts.most_common(40):
    print(
        f"{count:>3} | {subject}"
    )

print("\n=== ALL REMAINING REVIEW EMAILS ===")

for record in review_records:

    print("\n----------------------------------------")
    print("Email ID:", record["email_id"])
    print("Subject:", record["subject"])
    print("Sender:", record["sender"])
    print("Email Type:", record["email_type"])

REVIEW_FILE = "data/processed/job_relevance_manual_review.csv"

with open(
    REVIEW_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as csv_file:

    fieldnames = [
        "email_id",
        "subject",
        "sender",
        "email_type",
        "manual_relevance",
        "review_notes"
    ]

    writer = csv.DictWriter(
        csv_file,
        fieldnames=fieldnames
    )

    writer.writeheader()

    for record in review_records:

        writer.writerow(
            {
                "email_id": record["email_id"],
                "subject": record["subject"],
                "sender": record["sender"],
                "email_type": record["email_type"],
                "manual_relevance": "",
                "review_notes": ""
            }
        )

print(
    "\nManual review file created:",
    REVIEW_FILE
)

print(
    "Emails requiring manual review:",
    len(review_records)
)