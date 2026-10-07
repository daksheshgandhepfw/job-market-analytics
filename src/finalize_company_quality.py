import csv


INPUT_FILE = "data/processed/enriched_job_emails.csv"
OUTPUT_FILE = "data/processed/enriched_job_emails.csv"


# --------------------------------------------------
# VERIFIED COMPANY CORRECTIONS
# --------------------------------------------------

corrections = {
    # American Express
    "1a0777cb9cb92a35": "Amex",
    "1a06d1553f0f6558": "Amex",
    "1a063975c82b85ee": "Amex",
    "1a0638f5fefb72fe": "Amex",
    "1a0638c93e6eb06c": "Amex",
    "1a06386782f3995f": "Amex",
    "1a063832c0fd6e7f": "Amex",
    "1a0637af8721671e": "Amex",
    "1a0637762203a67e": "Amex",

    # Clearly identifiable employers
    "1a0729b72c8d231c": "Extreme Engineering Solutions",
    "1a06378fda1598f6": "Alpha Omega Integration",

    # T-Mobile
    "1a06374c5854abb7": "T-Mobile",
    "19ff28fb1744f1c2": "T-Mobile",
    "19ff288df195970c": "T-Mobile",

    # Providence
    "1a0636b94f438d36": "Providence",

    # Jobgether
    "1a06367af0dc188d": "Jobgether",
    "19ffc8cdd755083c": "Jobgether",
    "19ff283ebcffa461": "Jobgether",

    # LMI
    "1a0635fc7518e419": "LMI",

    # Emory
    "1a05dc48be5893de": "Emory",

    # AB InBev
    "1a03b3de6e01bcfe": "AB InBev",

    # Howmet Aerospace
    "1a0003d824c646f6": "Howmet Aerospace",

    # Boyd Gaming
    "19ffc9bde0d572b9": "Boyd Gaming",

    # State Street
    "19fed6806e852e0a": "State Street",

    # Textron
    "19d6a407971f7b8a": "Textron",

    # Perpay
    "19d4c910f6419cdb": "Perpay",
    "19d478c96299ab49": "Perpay",
    "19c92e00d185fd9c": "Perpay",

    # SpecterOps
    "19d4c89b31f6627c": "SpecterOps",

    # Omnicom Health
    "19d4793e0d6adfc5": "Omnicom Health",

    # Jefferson Health
    "19d187ebf98b4aea": "Jefferson Health",

    # Array Technologies
    "19cd9e26187c877d": "Array Technologies",

    # AMP
    "19c897ccdeb2ec16": "AMP",

    # AST SpaceMobile
    "19c897ccbdd4b52f": "AST SpaceMobile",
    "19c897748f4bb68f": "AST SpaceMobile",

    # EquipmentShare
    "19c897afbed6e519": "EquipmentShare",

    # ConvergeOne
    "19c7edb23a033187": "ConvergeOne",

    # Intuitive
    "19c2fbdb985ab1e1": "Intuitive",
    "19c2fb4705567289": "Intuitive",

    # Gen
    "19c2fab25dba48a5": "Gen",
}


# --------------------------------------------------
# READ
# --------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    fieldnames = reader.fieldnames
    records = list(reader)


# --------------------------------------------------
# APPLY VERIFIED CORRECTIONS
# --------------------------------------------------

corrected = 0

for record in records:

    email_id = record["email_id"]

    if email_id in corrections:

        old_company = record["company_name"]
        new_company = corrections[email_id]

        record["company_name"] = new_company
        record["company_source"] = "MANUAL_VERIFIED"

        corrected += 1

        print(
            f"{email_id}: "
            f"{old_company!r} -> {new_company!r}"
        )


# --------------------------------------------------
# WRITE BACK
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


print()
print(f"Corrected company values: {corrected}")
print(f"Output: {OUTPUT_FILE}")