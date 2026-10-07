import csv
from collections import Counter


EMAIL_RELEVANCE_FILE = "data/processed/email_relevance.csv"
MANUAL_REVIEW_FILE = "data/processed/job_relevance_manual_review.csv"
OUTPUT_FILE = "data/processed/final_email_relevance.csv"


# --------------------------------------------------
# LOAD MANUAL REVIEW DECISIONS
# --------------------------------------------------

manual_decisions = {}

with open(
    MANUAL_REVIEW_FILE,
    "r",
    encoding="utf-8"
) as csv_file:

    reader = csv.DictReader(csv_file)

    for record in reader:
        manual_decisions[record["email_id"]] = {
            "manual_relevance": record["manual_relevance"],
            "review_notes": record["review_notes"]
        }


# --------------------------------------------------
# LOAD AUTOMATED RELEVANCE RESULTS
# --------------------------------------------------

final_records = []

with open(
    EMAIL_RELEVANCE_FILE,
    "r",
    encoding="utf-8"
) as csv_file:

    reader = csv.DictReader(csv_file)

    for record in reader:

        automated_relevance = record["email_relevance"]

        # Use automatic result unless it required review
        if automated_relevance != "REVIEW":
            final_relevance = automated_relevance
            decision_source = "AUTOMATED"
            review_notes = ""

        else:
            manual = manual_decisions.get(record["email_id"])

            if manual:
                final_relevance = manual["manual_relevance"]
                decision_source = "MANUAL"
                review_notes = manual["review_notes"]

            else:
                final_relevance = "REVIEW"
                decision_source = "UNRESOLVED"
                review_notes = "No manual review decision found"

        final_records.append(
            {
                "email_id": record["email_id"],
                "subject": record["subject"],
                "sender": record["sender"],
                "email_type": record["email_type"],
                "automated_relevance": automated_relevance,
                "final_relevance": final_relevance,
                "decision_source": decision_source,
                "review_notes": review_notes
            }
        )


# --------------------------------------------------
# WRITE FINAL RELEVANCE DATASET
# --------------------------------------------------

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
        "automated_relevance",
        "final_relevance",
        "decision_source",
        "review_notes"
    ]

    writer = csv.DictWriter(
        csv_file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(final_records)


# --------------------------------------------------
# VALIDATE RESULTS
# --------------------------------------------------

counts = Counter(
    record["final_relevance"]
    for record in final_records
)

source_counts = Counter(
    record["decision_source"]
    for record in final_records
)

print(f"Total emails: {len(final_records)}")

print("\nFinal relevance:")
for relevance, count in counts.items():
    print(f"{relevance}: {count}")

print("\nDecision source:")
for source, count in source_counts.items():
    print(f"{source}: {count}")

print(f"\nCreated: {OUTPUT_FILE}")