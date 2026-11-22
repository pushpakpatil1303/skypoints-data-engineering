
from pathlib import Path
from uuid import uuid4

from parse_flat_file import parse_flat_file, validate_members
from snowflake_connection import get_snowflake_connection


BASE_DIR = Path(__file__).resolve().parent.parent
FILE_PATH = BASE_DIR / "data" / "sample" / "members_sample.txt"


def load_flat_file():
    df = parse_flat_file(FILE_PATH)
    errors = validate_members(df)

    if errors:
        raise ValueError("Validation failed:\n" + "\n".join(errors))

    batch_id = str(uuid4())

    columns = [
        "MEMBER_NAME", "MEMBER_ID", "ENROLLMENT_DATE",
        "LAST_FLIGHT_DATE", "TIER_CODE", "AGENT_NAME",
        "STATE", "COUNTRY", "POST_CODE", "DOB",
        "IS_ACTIVE", "SOURCE_FILE", "BATCH_ID"
    ]

    insert_sql = f"""
        INSERT INTO SKYPOINTS_DB.RAW.MEMBER_PROFILE
        ({", ".join(columns)})
        VALUES ({", ".join(["%s"] * len(columns))})
    """

    rows = []

    for _, row in df.iterrows():
        rows.append((
            row["Member_Name"],
            row["Member_Id"],
            row["Enrollment_Date"],
            row["Last_Flight_Date"],
            row["Tier_Code"],
            row["Agent_Name"],
            row["State"],
            row["Country"],
            None,
            row["DOB"],
            row["Is_Active"],
            FILE_PATH.name,
            batch_id
        ))

    with get_snowflake_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("BEGIN")

            try:
                cursor.execute(
                    """
                    DELETE FROM SKYPOINTS_DB.RAW.MEMBER_PROFILE
                    WHERE SOURCE_FILE = %s
                    """,
                    (FILE_PATH.name,)
                )

                cursor.executemany(insert_sql, rows)
                cursor.execute("COMMIT")

            except Exception:
                cursor.execute("ROLLBACK")
                raise

    print(f"Successfully loaded {len(rows)} flat-file records.")
    print(f"Source file: {FILE_PATH.name}")
    print(f"Batch ID: {batch_id}")


if __name__ == "__main__":
    load_flat_file()
