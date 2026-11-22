
from pathlib import Path
import csv
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
FILE_PATH = BASE_DIR / "data" / "sample" / "members_sample.txt"


def parse_flat_file(file_path):
    records = []
    headers = None

    with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file, delimiter="|")

        for line_number, row in enumerate(reader, start=1):
            if not row or not any(value.strip() for value in row):
                continue

            if row[0] == "":
                row = row[1:]

            record_type = row[0]
            values = row[1:]

            if record_type == "H":
                if headers is not None:
                    raise ValueError("Duplicate header record")

                headers = [value.strip() for value in values]

            elif record_type == "D":
                if headers is None:
                    raise ValueError(
                        f"Data record before header at line {line_number}"
                    )

                if len(values) != len(headers):
                    raise ValueError(
                        f"Column count mismatch at line {line_number}"
                    )

                records.append(dict(zip(headers, values)))

            else:
                raise ValueError(
                    f"Unknown record type at line {line_number}: {record_type}"
                )

    if headers is None:
        raise ValueError("Header record not found")

    return pd.DataFrame(records, columns=headers)

from datetime import datetime


def validate_members(df):
    errors = []

    required_columns = [
        "Member_Name",
        "Member_Id",
        "Enrollment_Date"
    ]

    max_lengths = {
        "Member_Name": 255,
        "Member_Id": 18,
        "Tier_Code": 5,
        "Agent_Name": 255,
        "State": 5,
        "Country": 5,
        "Is_Active": 1
    }

    for index, row in df.iterrows():
        row_number = index + 1

        for column in required_columns:
            if not str(row[column]).strip():
                errors.append(
                    f"Row {row_number}: Missing mandatory {column}"
                )

        for column, max_length in max_lengths.items():
            if len(str(row[column])) > max_length:
                errors.append(
                    f"Row {row_number}: {column} exceeds {max_length} characters"
                )

        for column, date_format in [
            ("Enrollment_Date", "%Y%m%d"),
            ("Last_Flight_Date", "%Y%m%d"),
            ("DOB", "%m%d%Y")
        ]:
            value = str(row[column]).strip()

            if value:
                try:
                    datetime.strptime(value, date_format)
                except ValueError:
                    errors.append(
                        f"Row {row_number}: Invalid {column}: {value}"
                    )

    if df["Member_Name"].duplicated().any():
        errors.append("Duplicate Member_Name found")

    return errors



if __name__ == "__main__":
    df = parse_flat_file(FILE_PATH)

    print("Total records:", len(df))
    print(df.to_string(index=False))

    validation_errors = validate_members(df)

    if validation_errors:
        print("\nValidation failed:")
        for error in validation_errors:
            print("-", error)
    else:
        print("\nValidation passed: All records are valid.")
