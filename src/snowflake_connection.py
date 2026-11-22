
import os
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

# Load Snowflake credentials from the project .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def get_snowflake_connection():
    # Create a connection using environment variables
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE")
    )


if __name__ == "__main__":
    # Test the connection and close it after use
    with get_snowflake_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT CURRENT_DATABASE(), CURRENT_WAREHOUSE(), CURRENT_ROLE()"
            )
            result = cursor.fetchone()
            print("Snowflake connection successful!")
            print("Database:", result[0])
            print("Warehouse:", result[1])
            print("Role:", result[2])
