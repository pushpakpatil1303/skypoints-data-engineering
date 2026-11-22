
from pathlib import Path
import pandas as pd

# Define the folder containing the source Excel files
DATA_FOLDER = Path(__file__).resolve().parent.parent / "data" / "sample"

# Map different source column names to a common structure
COLUMN_MAPPING = {
    "AUS": {
        "Unique ID": "MEMBER_ID",
        "Member Name": "MEMBER_NAME",
        "Tier Type": "TIER_CODE",
        "Date of Birth": "DOB",
        "Date of Enrollment": "ENROLLMENT_DATE",
        "Date of Flight": "LAST_FLIGHT_DATE"
    },
    "IND": {
        "ID": "MEMBER_ID",
        "Name": "MEMBER_NAME",
        "DOB": "DOB",
        "TierCode": "TIER_CODE",
        "EnrollmentDate": "ENROLLMENT_DATE",
        "Flight Date": "LAST_FLIGHT_DATE"
    },
    "USA": {
        "ID": "MEMBER_ID",
        "Name": "MEMBER_NAME",
        "TierCode": "TIER_CODE",
        "EnrollmentDate": "ENROLLMENT_DATE",
        "FlightDate": "LAST_FLIGHT_DATE"
    }
}

# Define the standardized columns required for all countries
STANDARD_COLUMNS = [
    "MEMBER_ID",
    "MEMBER_NAME",
    "TIER_CODE",
    "DOB",
    "ENROLLMENT_DATE",
    "LAST_FLIGHT_DATE",
    "COUNTRY",
    "SOURCE_FILE"
]


def load_member_file(country):
    # Read the source Excel file and preserve original values as strings
    file_path = DATA_FOLDER / f"{country}.xlsx"
    df = pd.read_excel(file_path, dtype=str)

    # Standardize column names using the country-specific mapping
    df = df.rename(columns=COLUMN_MAPPING[country])

    # Add country and source file information for tracking
    df["COUNTRY"] = country
    df["SOURCE_FILE"] = file_path.name

    # Add missing optional columns without losing source records
    for column in STANDARD_COLUMNS:
        if column not in df.columns:
            df[column] = None

    return df[STANDARD_COLUMNS]


# Execute ingestion for all three countries
if __name__ == "__main__":
    for country in ["AUS", "IND", "USA"]:
        members = load_member_file(country)

        print(f"\n{country} — Standardized Data")
        print(members.to_string(index=False))
