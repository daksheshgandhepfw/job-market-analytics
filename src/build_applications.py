import pandas as pd
from collections import defaultdict


INPUT_FILE = "data/processed/enriched_job_reference_ids.csv"

OUTPUT_FILE = "data/processed/applications_deduplicated.csv"
OUTPUT_AUDIT = "data/processed/application_dedup_audit.txt"


# ============================================================
# BASIC CLEANING
# ============================================================

def clean(value):
    if pd.isna(value):
        return ""

    return str(value).strip()


def normalize(value):
    """
    Normalize text for comparison only.

    Original company names, job titles, and reference IDs
    are preserved in the final dataset.
    """

    value = clean(value).lower()
    value = " ".join(value.split())

    return value


def parse_date(value):
    """
    Parse Gmail email dates safely.

    Some Gmail dates contain a timezone abbreviation
    in parentheses, for example:

    Mon, 30 Mar 2026 17:12:16 -0400 (EDT)

    The numeric timezone offset (-0400) is sufficient,
    so the trailing abbreviation is removed before parsing.
    """

    if pd.isna(value):
        return pd.NaT

    value = str(value).strip()

    # Remove trailing timezone abbreviation such as:
    # (EDT), (EST), (PDT), (PST), (UTC)
    value = pd.Series([value]).str.replace(
        r"\s+\([A-Z]{2,5}\)$",
        "",
        regex=True
    ).iloc[0]

    return pd.to_datetime(
        value,
        errors="coerce",
        utc=True
    )


# ============================================================
# APPLICATION-LEVEL FIELD LOGIC
# ============================================================

def get_application_date(group):
    """
    Application date comes ONLY from the earliest
    Application Confirmation email.

    A rejection date must never become the application date.
    """

    confirmations = group[
        group["email_type"] == "Application Confirmation"
    ].copy()

    if confirmations.empty:
        return pd.NaT

    return confirmations["_date"].min()


def get_final_status(group):
    """
    Current V1 status logic.

    If any rejection exists:
        Rejected

    Otherwise:
        Applied

    Assessment / Interview / Offer can be incorporated later
    if those email types are added to the dataset.
    """

    email_types = set(
        group["email_type"]
        .dropna()
        .astype(str)
    )

    if "Rejection" in email_types:
        return "Rejected"

    return "Applied"


def get_response_status(group):
    """
    Application confirmations are NOT considered employer
    responses.

    A rejection counts as a response.
    """

    if (
        group["email_type"] == "Rejection"
    ).any():
        return "Responded"

    return "No Response"


def get_first_response_date(group):
    """
    Return the earliest actual employer response.

    Currently the classified response type available
    in this dataset is Rejection.
    """

    responses = group[
        group["email_type"] == "Rejection"
    ].copy()

    if responses.empty:
        return pd.NaT

    return responses["_date"].min()


def choose_reference_id(group):
    """
    Select the reference ID for an application.

    Blank values are ignored.

    If exactly one unique non-empty reference ID exists,
    return it.

    Different reference IDs should never intentionally
    reach the same application group.
    """

    refs = [
        clean(value)
        for value in group["job_reference_id"]
        if clean(value)
    ]

    refs = list(dict.fromkeys(refs))

    if len(refs) == 1:
        return refs[0]

    return ""


def choose_company(group):
    """
    Select the first available company name.

    Because metadata enrichment has already been performed,
    company values should generally be available.
    """

    values = [
        clean(value)
        for value in group["company_name"]
        if clean(value)
    ]

    if not values:
        return ""

    return values[0]


def choose_title(group):
    """
    Select the first available job title.

    Missing titles remain missing rather than being guessed.
    """

    values = [
        clean(value)
        for value in group["job_title"]
        if clean(value)
    ]

    if not values:
        return ""

    return values[0]


# ============================================================
# CONSERVATIVE NO-REFERENCE MATCHING
# ============================================================

def should_merge_confirmation_rejection(row1, row2):
    """
    Merge two no-reference-ID emails only when:

    1. Company matches.
    2. Exact normalized job title matches.
    3. Company is present.
    4. Job title is present.
    5. Neither email contains a reference ID.
    6. One email is Application Confirmation.
    7. The other email is Rejection.

    Date proximity alone is NEVER sufficient evidence.
    """

    if row1["_company"] != row2["_company"]:
        return False

    if not row1["_company"]:
        return False

    if row1["_title"] != row2["_title"]:
        return False

    if not row1["_title"]:
        return False

    if row1["_ref"] or row2["_ref"]:
        return False

    email_types = {
        clean(row1["email_type"]),
        clean(row2["email_type"])
    }

    return email_types == {
        "Application Confirmation",
        "Rejection"
    }


# ============================================================
# MAIN
# ============================================================

def main():

    df = pd.read_csv(INPUT_FILE)

    # --------------------------------------------------------
    # Create comparison-only fields
    # --------------------------------------------------------

    df["_company"] = df[
        "company_name"
    ].apply(normalize)

    df["_title"] = df[
        "job_title"
    ].apply(normalize)

    df["_ref"] = df[
        "job_reference_id"
    ].apply(normalize)

    df["_date"] = df[
        "email_date"
    ].apply(parse_date)

    # --------------------------------------------------------
    # Initially every email represents its own application.
    # --------------------------------------------------------

    groups = {
        idx: [idx]
        for idx in df.index
    }

    email_to_group = {
        idx: idx
        for idx in df.index
    }

    merge_log = []

    # --------------------------------------------------------
    # GROUP MERGE HELPER
    # --------------------------------------------------------

    def merge_groups(group_a, group_b, reason):

        if group_a == group_b:
            return group_a

        # Use the smaller original index as the
        # canonical internal group ID.
        keep = min(group_a, group_b)
        remove = max(group_a, group_b)

        remove_members = groups[remove]

        groups[keep].extend(
            remove_members
        )

        for email_idx in remove_members:
            email_to_group[email_idx] = keep

        del groups[remove]

        merge_log.append({
            "kept_group": keep,
            "removed_group": remove,
            "reason": reason
        })

        return keep

    # ========================================================
    # PASS 1
    # SAME NON-EMPTY REFERENCE ID
    # ========================================================

    ref_to_indexes = defaultdict(list)

    for idx, row in df.iterrows():

        ref = row["_ref"]

        if ref:
            ref_to_indexes[ref].append(idx)

    for ref, indexes in ref_to_indexes.items():

        if len(indexes) < 2:
            continue

        base_group = email_to_group[
            indexes[0]
        ]

        for idx in indexes[1:]:

            other_group = email_to_group[
                idx
            ]

            base_group = merge_groups(
                base_group,
                other_group,
                f"SAME_REFERENCE_ID:{ref}"
            )

    # ========================================================
    # PASS 2
    # SAME COMPANY + EXACT TITLE
    # CONFIRMATION -> REJECTION
    # BOTH WITHOUT REFERENCE IDS
    # ========================================================

    candidate_groups = defaultdict(list)

    for idx, row in df.iterrows():

        # Reference-ID cases are handled separately.
        if row["_ref"]:
            continue

        # Never match using company alone.
        if not row["_company"]:
            continue

        # Never match when title is missing.
        if not row["_title"]:
            continue

        key = (
            row["_company"],
            row["_title"]
        )

        candidate_groups[key].append(
            idx
        )

    for key, indexes in candidate_groups.items():

        confirmations = []
        rejections = []

        for idx in indexes:

            email_type = clean(
                df.loc[
                    idx,
                    "email_type"
                ]
            )

            if (
                email_type
                == "Application Confirmation"
            ):
                confirmations.append(
                    idx
                )

            elif email_type == "Rejection":
                rejections.append(
                    idx
                )

        # ----------------------------------------------------
        # Conservative matching:
        #
        # EXACTLY one confirmation
        # +
        # EXACTLY one rejection
        #
        # Multiple confirmations remain separate.
        # Multiple rejections remain separate.
        # ----------------------------------------------------

        if (
            len(confirmations) == 1
            and len(rejections) == 1
        ):

            confirmation_idx = (
                confirmations[0]
            )

            rejection_idx = (
                rejections[0]
            )

            row1 = df.loc[
                confirmation_idx
            ]

            row2 = df.loc[
                rejection_idx
            ]

            if should_merge_confirmation_rejection(
                row1,
                row2
            ):

                group_a = email_to_group[
                    confirmation_idx
                ]

                group_b = email_to_group[
                    rejection_idx
                ]

                merge_groups(
                    group_a,
                    group_b,
                    "COMPANY_TITLE_CONFIRMATION_REJECTION"
                )

    # ========================================================
    # PASS 3
    # MANUALLY VERIFIED ASYMMETRIC MATCHES
    # ========================================================
    #
    # These cases have been manually reviewed.
    #
    # One email may contain a reliable reference ID while
    # another email from the SAME application does not.
    #
    # We intentionally do NOT turn this into a generic rule.
    # Company + title alone is not sufficient evidence when
    # one side contains a reference ID.
    #
    # Keeping these explicit prevents false merges.
    # ========================================================

    verified_email_matches = [

        # ----------------------------------------------------
        # Jabil
        #
        # Confirmation:
        #   Business Intelligence Analyst and Developer I
        #   no extracted reference ID
        #
        # Rejection:
        #   same company
        #   same exact job title
        #   reference ID J2462394
        #
        # Manually verified as the same application.
        # ----------------------------------------------------

        (
            "1a045baeb0eb90f0",
            "1a0caa43fb2c7ae0",
        ),

    ]

    # Map Gmail email IDs to dataframe indexes.

    email_id_to_index = {
        clean(row["email_id"]): idx
        for idx, row in df.iterrows()
    }

    for (
        email_id_a,
        email_id_b
    ) in verified_email_matches:

        # Do not crash if an email disappears from
        # a future version of the dataset.

        if (
            email_id_a
            not in email_id_to_index
            or
            email_id_b
            not in email_id_to_index
        ):
            continue

        idx_a = email_id_to_index[
            email_id_a
        ]

        idx_b = email_id_to_index[
            email_id_b
        ]

        group_a = email_to_group[
            idx_a
        ]

        group_b = email_to_group[
            idx_b
        ]

        merge_groups(
            group_a,
            group_b,
            "MANUAL_VERIFIED_MATCH"
        )

    # ========================================================
    # SAFETY VALIDATION
    # ========================================================
    #
    # Verify that no application group accidentally contains
    # multiple DIFFERENT non-empty reference IDs.
    #
    # If this ever happens, stop the script rather than
    # silently creating a false application.
    # ========================================================

    for group_id, indexes in groups.items():

        group = df.loc[indexes]

        refs = {
            clean(value)
            for value in group[
                "job_reference_id"
            ]
            if clean(value)
        }

        if len(refs) > 1:

            raise ValueError(
                "MATCHING SAFETY ERROR: "
                f"group {group_id} contains "
                f"multiple reference IDs: "
                f"{sorted(refs)}"
            )

    # ========================================================
    # BUILD APPLICATION-LEVEL RECORDS
    # ========================================================

    application_rows = []

    sorted_groups = sorted(
        groups.values(),
        key=lambda indexes: min(indexes)
    )

    for number, indexes in enumerate(
        sorted_groups,
        start=1
    ):

        group = df.loc[
            indexes
        ].copy()

        group = group.sort_values(
            "_date"
        )

        application_id = (
            f"APP{number:04d}"
        )

        application_date = (
            get_application_date(
                group
            )
        )

        first_response_date = (
            get_first_response_date(
                group
            )
        )

        status = get_final_status(
            group
        )

        response_status = (
            get_response_status(
                group
            )
        )

        reference_id = (
            choose_reference_id(
                group
            )
        )

        company = choose_company(
            group
        )

        title = choose_title(
            group
        )

        email_ids = "|".join(
            group[
                "email_id"
            ]
            .astype(str)
            .tolist()
        )

        application_rows.append({

            "application_id":
                application_id,

            "company_name":
                company,

            "job_title":
                title,

            "job_reference_id":
                reference_id,

            "application_date":
                (
                    application_date
                    .date()
                    .isoformat()
                    if pd.notna(
                        application_date
                    )
                    else ""
                ),

            "status":
                status,

            "response_status":
                response_status,

            "first_response_date":
                (
                    first_response_date
                    .date()
                    .isoformat()
                    if pd.notna(
                        first_response_date
                    )
                    else ""
                ),

            "email_count":
                len(group),

            "email_ids":
                email_ids,
        })

    applications = pd.DataFrame(
        application_rows
    )

    # ========================================================
    # FINAL DATASET VALIDATION
    # ========================================================

    # Application IDs must be unique.

    if applications[
        "application_id"
    ].duplicated().any():

        raise ValueError(
            "Duplicate application IDs detected."
        )

    # No application can contain zero emails.

    if (
        applications[
            "email_count"
        ] < 1
    ).any():

        raise ValueError(
            "Application with zero emails detected."
        )

    # Total emails represented by applications
    # must equal original input count.

    represented_email_count = (
        applications[
            "email_count"
        ].sum()
    )

    if represented_email_count != len(df):

        raise ValueError(
            "Email-count validation failed. "
            f"Input emails: {len(df)}, "
            "represented emails: "
            f"{represented_email_count}"
        )

    # --------------------------------------------------------
    # Save application dataset
    # --------------------------------------------------------

    applications.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ========================================================
    # AUDIT REPORT
    # ========================================================

    multi_email_apps = applications[
        applications[
            "email_count"
        ] > 1
    ]

    with open(
        OUTPUT_AUDIT,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "=== APPLICATION DEDUPLICATION AUDIT ===\n\n"
        )

        f.write(
            f"Input emails: {len(df)}\n"
        )

        f.write(
            "Unique applications: "
            f"{len(applications)}\n"
        )

        f.write(
            "Emails merged away: "
            f"{len(df) - len(applications)}\n"
        )

        f.write(
            "Applications containing multiple emails: "
            f"{len(multi_email_apps)}\n\n"
        )

        # ----------------------------------------------------
        # Status counts
        # ----------------------------------------------------

        f.write(
            "--- STATUS COUNTS ---\n"
        )

        for status, count in (
            applications[
                "status"
            ]
            .value_counts()
            .items()
        ):

            f.write(
                f"{status}: {count}\n"
            )

        # ----------------------------------------------------
        # Response counts
        # ----------------------------------------------------

        f.write(
            "\n--- RESPONSE STATUS COUNTS ---\n"
        )

        for status, count in (
            applications[
                "response_status"
            ]
            .value_counts()
            .items()
        ):

            f.write(
                f"{status}: {count}\n"
            )

        # ----------------------------------------------------
        # Merge log
        # ----------------------------------------------------

        f.write(
            "\n--- MERGE LOG ---\n"
        )

        for item in merge_log:

            f.write(
                f"{item['reason']} | "
                f"group "
                f"{item['removed_group']} "
                f"-> "
                f"{item['kept_group']}\n"
            )

        # ----------------------------------------------------
        # Multi-email applications
        # ----------------------------------------------------

        f.write(
            "\n--- MULTI-EMAIL APPLICATIONS ---\n"
        )

        for _, row in (
            multi_email_apps.iterrows()
        ):

            f.write(
                "\n"
                + "=" * 80
                + "\n"
            )

            f.write(
                "Application ID: "
                f"{row['application_id']}\n"
            )

            f.write(
                "Company: "
                f"{row['company_name']}\n"
            )

            f.write(
                "Job Title: "
                f"{row['job_title']}\n"
            )

            f.write(
                "Reference ID: "
                f"{row['job_reference_id']}\n"
            )

            f.write(
                "Status: "
                f"{row['status']}\n"
            )

            f.write(
                "Email Count: "
                f"{row['email_count']}\n"
            )

            f.write(
                "Email IDs: "
                f"{row['email_ids']}\n"
            )

    # ========================================================
    # TERMINAL SUMMARY
    # ========================================================

    print(
        "Input job-related emails:",
        len(df)
    )

    print(
        "Unique applications:",
        len(applications)
    )

    print(
        "Emails merged away:",
        len(df) - len(applications)
    )

    print(
        "Multi-email applications:",
        len(multi_email_apps)
    )

    print(
        "\nStatus counts:"
    )

    print(
        applications[
            "status"
        ].value_counts()
    )

    print(
        "\nResponse status counts:"
    )

    print(
        applications[
            "response_status"
        ].value_counts()
    )

    print(
        "\nCreated:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        OUTPUT_AUDIT
    )


if __name__ == "__main__":
    main()