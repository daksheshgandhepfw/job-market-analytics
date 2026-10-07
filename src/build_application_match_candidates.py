import pandas as pd
from collections import defaultdict

INPUT_FILE = "data/processed/enriched_job_reference_ids.csv"

OUTPUT_SUMMARY = "data/processed/application_match_profile.txt"
OUTPUT_REVIEW = "data/processed/application_match_review.csv"


def clean(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_text(value):
    """
    Conservative normalization for comparison only.
    Original values remain untouched.
    """
    value = clean(value).lower()
    value = " ".join(value.split())
    return value


def main():
    df = pd.read_csv(INPUT_FILE)

    # ---------------------------------------------------------
    # Normalize fields for comparison only
    # ---------------------------------------------------------

    df["_company"] = df["company_name"].apply(normalize_text)
    df["_title"] = df["job_title"].apply(normalize_text)
    df["_ref"] = df["job_reference_id"].apply(normalize_text)

    df["_date"] = pd.to_datetime(
        df["email_date"],
        errors="coerce",
        utc=True
    )

    # ---------------------------------------------------------
    # CATEGORY 1
    # Same non-empty reference ID
    # ---------------------------------------------------------

    ref_groups = defaultdict(list)

    for idx, row in df.iterrows():
        ref = row["_ref"]

        if ref:
            ref_groups[ref].append(idx)

    repeated_ref_groups = {
        ref: indexes
        for ref, indexes in ref_groups.items()
        if len(indexes) > 1
    }

    # ---------------------------------------------------------
    # CATEGORY 2
    # Same company + title where reference IDs do not already
    # give us a deterministic answer.
    # ---------------------------------------------------------

    company_title_groups = defaultdict(list)

    for idx, row in df.iterrows():

        company = row["_company"]
        title = row["_title"]

        if company and title:
            key = (company, title)
            company_title_groups[key].append(idx)

    repeated_company_title = {
        key: indexes
        for key, indexes in company_title_groups.items()
        if len(indexes) > 1
    }

    # ---------------------------------------------------------
    # Build manual-review candidates
    # ---------------------------------------------------------

    review_rows = []

    for (company, title), indexes in repeated_company_title.items():

        group = df.loc[indexes].copy()

        refs = sorted(
            set(
                ref
                for ref in group["_ref"]
                if ref
            )
        )

        # If multiple different reference IDs exist,
        # these are definitely different applications.
        if len(refs) > 1:
            decision = "DIFFERENT_APPLICATIONS"
            reason = "Different non-empty reference IDs"

        # If all records share exactly one reference ID,
        # reference ID already gives us the answer.
        elif len(refs) == 1 and group["_ref"].ne("").all():
            decision = "SAME_APPLICATION"
            reason = "Same non-empty reference ID"

        # Otherwise company/title similarity alone is not
        # enough to merge automatically.
        else:
            decision = "REVIEW"
            reason = "Repeated company/title without deterministic reference-ID evidence"

        for _, row in group.iterrows():

            review_rows.append({
                "email_id": clean(row.get("email_id")),
                "email_date": clean(row.get("email_date")),
                "email_type": clean(row.get("email_type")),
                "company_name": clean(row.get("company_name")),
                "job_title": clean(row.get("job_title")),
                "job_reference_id": clean(
                    row.get("job_reference_id")
                ),
                "reference_id_source": clean(
                    row.get("job_reference_id_source")
                ),
                "subject": clean(row.get("subject")),
                "candidate_decision": decision,
                "decision_reason": reason,
            })

    review_df = pd.DataFrame(review_rows)

    if not review_df.empty:
        review_df = review_df.sort_values(
            [
                "candidate_decision",
                "company_name",
                "job_title",
                "email_date"
            ]
        )

    review_df.to_csv(
        OUTPUT_REVIEW,
        index=False
    )

    # ---------------------------------------------------------
    # Missing-title population
    # ---------------------------------------------------------

    missing_title = df[
        df["_title"] == ""
    ]

    missing_title_no_ref = missing_title[
        missing_title["_ref"] == ""
    ]

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    with open(
        OUTPUT_SUMMARY,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "=== APPLICATION MATCHING PROFILE ===\n\n"
        )

        f.write(
            f"Total job-related emails: {len(df)}\n\n"
        )

        f.write(
            "--- REFERENCE ID MATCHING ---\n"
        )

        f.write(
            f"Emails with reference ID: "
            f"{(df['_ref'] != '').sum()}\n"
        )

        f.write(
            f"Unique reference IDs: "
            f"{df.loc[df['_ref'] != '', '_ref'].nunique()}\n"
        )

        f.write(
            f"Repeated reference-ID groups: "
            f"{len(repeated_ref_groups)}\n"
        )

        f.write(
            "Emails belonging to repeated reference-ID "
            f"groups: "
            f"{sum(len(v) for v in repeated_ref_groups.values())}\n\n"
        )

        f.write(
            "--- COMPANY + TITLE CANDIDATES ---\n"
        )

        f.write(
            f"Repeated company-title groups: "
            f"{len(repeated_company_title)}\n"
        )

        f.write(
            "Emails belonging to repeated company-title "
            f"groups: "
            f"{sum(len(v) for v in repeated_company_title.values())}\n\n"
        )

        f.write(
            "--- MISSING TITLE POPULATION ---\n"
        )

        f.write(
            f"Emails missing title: "
            f"{len(missing_title)}\n"
        )

        f.write(
            "Missing-title emails without reference ID: "
            f"{len(missing_title_no_ref)}\n\n"
        )

        if not review_df.empty:

            f.write(
                "--- CANDIDATE DECISIONS ---\n"
            )

            counts = (
                review_df["candidate_decision"]
                .value_counts()
            )

            for decision, count in counts.items():
                f.write(
                    f"{decision}: {count} emails\n"
                )

    print("Total emails:", len(df))

    print(
        "Emails with reference ID:",
        (df["_ref"] != "").sum()
    )

    print(
        "Repeated reference-ID groups:",
        len(repeated_ref_groups)
    )

    print(
        "Repeated company-title groups:",
        len(repeated_company_title)
    )

    print(
        "Emails requiring candidate analysis:",
        len(review_df)
    )

    if not review_df.empty:
        print("\nCandidate decisions:")
        print(
            review_df[
                "candidate_decision"
            ].value_counts()
        )

    print("\nCreated:")
    print(OUTPUT_SUMMARY)
    print(OUTPUT_REVIEW)


if __name__ == "__main__":
    main()