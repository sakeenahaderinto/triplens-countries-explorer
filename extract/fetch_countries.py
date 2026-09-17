import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from minio import Minio

load_dotenv()

RESTCOUNTRIES_API_KEY = os.getenv("RESTCOUNTRIES_API_KEY")

URL = 'https://api.restcountries.com/countries/v5'

RESPONSE_FIELDS = [
    "names.common", "names.official",
    "codes.alpha_2", "codes.alpha_3",
    "region", "subregion",
    "capitals", "landlocked",
    "borders", "population",
    "languages", "currencies",
    "calling_codes", "timezones",
    "flag.emoji", "car.side", "unit.measurement",
]

raw_path = Path("data/raw") / f"countries_{datetime.now(tz=UTC).strftime("%Y%m%d")}.json"

def fetch_data():
    all_countries = []
    offset = 0
    has_more = True

    headers = {'Authorization': f'Bearer {RESTCOUNTRIES_API_KEY}'}
    

    while has_more:

        params = {"response_fields": ",".join(RESPONSE_FIELDS), "limit": 100, "offset": offset}
        print(f"fetching from offset: {params["offset"]}")
        response = requests.get(URL, headers=headers, params=params)
        if response.status_code != 200:
            return response.raise_for_status()
        data = response.json()
        objects = data["data"]["objects"]
        all_countries.extend(objects)
        has_more = data["data"]["meta"].get("more", False)
        offset += params["limit"]
        time.sleep(1)

    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(json.dumps(all_countries, indent=2))
    print(f"written {len(all_countries)} records to {raw_path}")


def upload_to_minio():
    client = Minio(
        endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        access_key=os.getenv("MINIO_ROOT_USER"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
        secure=False,  # False because local MinIO runs on HTTP, not HTTPS
    )

    if not client.bucket_exists("triplens-raw"):
        client.make_bucket("triplens-raw")

    client.fput_object(bucket_name="triplens-raw",
                       object_name=f"countries/dt={datetime.now(tz=UTC).strftime('%Y-%m-%d')}/countries.json",
                       file_path=raw_path)

    print("successfully uploaded to MinIO.")



if __name__ == "__main__":
    fetch_data()
    upload_to_minio()
