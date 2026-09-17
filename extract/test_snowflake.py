import os

import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    role=os.getenv("SNOWFLAKE_ROLE", "TRIPLENS_ROLE"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "TRIPLENS_WH"),
    database=os.getenv("SNOWFLAKE_DATABASE", "TRIPLENS"),
    schema=os.getenv("SNOWFLAKE_SCHEMA", "RAW"),
)

cursor = conn.cursor()
cursor.execute("SELECT CURRENT_VERSION()")
version = cursor.fetchone()
print(f"Connected successfully to Snowflake! Version: {version[0]}")
cursor.close()
conn.close()