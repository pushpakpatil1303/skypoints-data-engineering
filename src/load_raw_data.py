
from datetime import datetime
from uuid import uuid4

import pandas as pd

from ingestion import load_member_file
from snowflake_connection import get_snowflake_connection


# Convert missing values to NULL while preserving source date strings
def prepare_value(value):
    if pd.isna(value):
        return None
    return str(value).strip()


# Load each source file into the RAW table
def load_raw_data():
    batch_id = str(uuid4())
    total_records = 0

    insert_sql = """
        INSERT INTO SKYPOINTS_DB.RAW.MEMBER_PROFILE (
            MEMBER_ID, MEMBER_NAME, TIER_CODE, DOB,
            ENROLLMENT_DATE, LAST_FLIGHT_DATE,
            COUNTRY, SOURCE_FILE, BATCH_ID
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    with get_snowflake_connection() as conn:
        conn.autocommit(False)

        try:
            with conn.cursor() as cursor:
                for country in ["AUS", "IND", "USA"]:
                    df = load_member_file(country)

                    records = [
                        tuple(prepare_value(value) for value in row)
                        + (batch_id,)
                        for row in df[
                            [
                                "MEMBER_ID",
                                "MEMBER_NAME",
                                "TIER_CODE",
                                "DOB",
                                "ENROLLMENT_DATE",
                                "LAST_FLIGHT_DATE",
                                "COUNTRY",
                                "SOURCE_FILE"
                            ]
                        ].itertuples(index=False, name=None)
                    ]

                    cursor.execute(
                        """
                        DELETE FROM SKYPOINTS_DB.RAW.MEMBER_PROFILE
                        WHERE SOURCE_FILE = %s
                        """,
                        (f"{country}.xlsx",)
                    )

                    cursor.executemany(insert_sql, records)

                    total_records += len(records)
                    print(f"{country}: {len(records)} records loaded")

            conn.commit()

        except Exception:
            conn.rollback()
            raise

    print(f"\nTotal records loaded: {total_records}")
    print(f"Batch ID: {batch_id}")


if __name__ == "__main__":
    load_raw_data()
