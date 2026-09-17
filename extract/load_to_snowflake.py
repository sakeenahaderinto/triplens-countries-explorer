import os
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv
from minio import Minio

load_dotenv()

client = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=False,
)

def load_to_snowflake():
    objects = list(client.list_objects("triplens-raw", prefix="countries/", recursive=True))
    latest_object = max(objects, key=lambda obj: obj.last_modified)

    local_staging_path = Path("data/staging/countries.json")
    local_staging_path.parent.mkdir(parents=True, exist_ok=True)

    client.fget_object("triplens-raw", latest_object.object_name, str(local_staging_path))
    print(f"Downloaded {latest_object.object_name} from MinIO to {local_staging_path}")

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
    cursor.execute("TRUNCATE TABLE TRIPLENS.RAW.COUNTRIES_RAW")
    cursor.execute(f"PUT file://{local_staging_path.resolve()} @%COUNTRIES_RAW AUTO_COMPRESS=TRUE OVERWRITE=TRUE")
    cursor.execute("""
    COPY INTO TRIPLENS.RAW.COUNTRIES_RAW (payload, loaded_at)
    FROM (
        SELECT $1, CURRENT_TIMESTAMP()
        FROM @%COUNTRIES_RAW
    )
    FILE_FORMAT = (TYPE = 'JSON' STRIP_OUTER_ARRAY = TRUE)
    ON_ERROR = 'ABORT_STATEMENT';
    """)

    cursor.execute("REMOVE @%COUNTRIES_RAW")

    cursor.execute("SELECT COUNT(*) FROM TRIPLENS.RAW.COUNTRIES_RAW")
    print(f"Total rows loaded: {cursor.fetchone()[0]}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    load_to_snowflake()