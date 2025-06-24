import os
import pandas as pd
import boto3
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# --- Configuration ---
# MySQL Database settings
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))  # Defaults to 3306 if not set
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_TABLE = os.getenv("MYSQL_TABLE")

# AWS S3 settings
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION_NAME = os.getenv("AWS_REGION_NAME", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET")

# Local directory to temporarily store Parquet files
LOCAL_PARQUET_DIR = os.getenv("LOCAL_PARQUET_DIR", "parquet_files/")
# Variable for the timestamp column used for grouping
TIMESTAMP_COLUMN = os.getenv("TIMESTAMP_COLUMN", "created_at")


# Validate required environment variables
required_vars = [
    MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_TABLE,
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET
]
if not all(required_vars):
    raise EnvironmentError("Missing one or more required environment variables.")


def export_to_parquet():
    """
    Export MySQL table data to Parquet files grouped by TIMESTAMP_COLUMN` date,
    then upload them to S3 using a structured path.
    """
    # Create a connection to the MySQL database
    engine = create_engine(
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )

    # Create a temporary local directory to store Parquet files
    os.makedirs(LOCAL_PARQUET_DIR, exist_ok=True)

    chunk_size = 10000  # Number of rows per batch
    offset = 0
    file_counter = 0

    while True:
        # Fetch a chunk of data from the table
        query = f"SELECT * FROM {MYSQL_TABLE} LIMIT {chunk_size} OFFSET {offset}"
        chunk = pd.read_sql(query, engine)

        if chunk.empty:
            print("No more data to export.")
            break

        # Convert TIMESTAMP_COLUMN to datetime and group by day
        chunk[TIMESTAMP_COLUMN] = pd.to_datetime(chunk[TIMESTAMP_COLUMN])
        grouped = chunk.groupby(chunk[TIMESTAMP_COLUMN].dt.to_period('D'))

        for period, group in grouped:
            # Format S3 path using year/month/day
            year = period.year
            month = f"{period.month:02d}"
            day = f"{period.day:02d}"
            s3_key_prefix = f"{S3_BUCKET}/year={year}/month={month}/day={day}/"

            # Save as a local Parquet file
            parquet_file = f"{LOCAL_PARQUET_DIR}data-{file_counter:04d}.parquet"
            group.to_parquet(parquet_file, engine="pyarrow", index=False)
            print(f"Exported {len(group)} rows to {parquet_file}")

            # Upload to S3 and delete local file
            s3_key = f"{s3_key_prefix}data-{file_counter:04d}.parquet"
            upload_to_s3(parquet_file, s3_key)
            os.remove(parquet_file)

            file_counter += 1

        offset += chunk_size


def upload_to_s3(file_path, s3_key):
    """
    Uploads a local file to AWS S3 at the given key path.
    """
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION_NAME
    )
    s3_client = session.client('s3')

    try:
        s3_client.upload_file(file_path, S3_BUCKET, s3_key)
        print(f"Uploaded {file_path} to s3://{S3_BUCKET}/{s3_key}")
    except Exception as e:
        print(f"Failed to upload {file_path}: {e}")


# Entry point
if __name__ == "__main__":
    export_to_parquet()
