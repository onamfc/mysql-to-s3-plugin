# MySQL to S3 Exporter

This Python script extracts data from a MySQL database in chunks, converts the data to Parquet files, organizes the files based on a `TIMESTAMP_COLUMN` timestamp, and uploads them to an Amazon S3 bucket.

## Table of Contents
1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Code Explanation](#code-explanation)
7. [Notes](#notes)

---

## Features
- Fetch data from a MySQL database in chunks of configurable size.
- Save each chunk as a Parquet file.
- Group data by `TIMESTAMP_COLUMN` (per day) to organize files into a directory structure.
- Upload the generated Parquet files to a specified Amazon S3 bucket.
- Clean up temporary local files after successful upload.

---

## Requirements
Ensure the following tools and libraries are installed:

- Python 3.7+
- MySQL Database
- Amazon S3 Bucket
- Libraries:
  - `pandas`
  - `boto3`
  - `sqlalchemy`
  - `pyarrow`
  - `pymysql`

---

## Installation

1. **Clone this repository**
   ```
   git clone https://github.com/onamfc/mysql-to-s3-plugin.git
   cd mysql-to-s3-plugin
   ```

2. **Create a virtual environment** (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```
   pip install pandas boto3 sqlalchemy pyarrow pymysql
   ```

---

## Configuration
Update the following configurations in the script:

### MySQL Configuration
Replace the placeholders in the code with your MySQL database details:
```
MYSQL_HOST = 'your-mysql-host'
MYSQL_PORT = 3306  # Update if your MySQL uses a different port
MYSQL_USER = 'your-username'
MYSQL_PASSWORD = 'your-password'
MYSQL_DATABASE = 'your-database'
MYSQL_TABLE = 'your-table'
```

### S3 Configuration
Replace these with your S3 bucket details and AWS credentials:
```
S3_BUCKET = 'your-s3-bucket-name'
LOCAL_PARQUET_DIR = 'parquet_files/'  # Temporary directory
```

For AWS authentication:
```
aws_access_key_id='your-access-key'
aws_secret_access_key='your-secret-key'
region_name='your-region'  # Example: 'us-east-1'
```


If your table uses a different timestamp column for grouping (other than `created_at`), you can override it:

```
TIMESTAMP_COLUMN=created_at  # or e.g., 'timestamp' or 'log_date'
```

---

## Usage

Run the script:
```
python your_script_name.py
```

The script will:
1. Fetch data from the specified MySQL table in chunks.
2. Group the data by the `TIMESTAMP_COLUMN` env var.
3. Save grouped data to local Parquet files.
4. Upload the Parquet files to the configured S3 bucket in the following directory structure:
   ```
   developer_logs/year=<year>/month=<month>/day=<day>/data-<file_number>.parquet
   ```
5. Delete the temporary Parquet files locally after upload.

---

## Code Explanation

1. **Data Fetching**:
   - The script fetches data in chunks (default: 10,000 rows) using MySQL queries with `LIMIT` and `OFFSET`.
   - Adjust the `chunk_size` to process larger or smaller chunks.

2. **Parquet Conversion**:
   - Data is grouped by the `TIMESTAMP_COLUMN` (daily).
   - The Parquet file format is used for efficient storage and performance.

3. **S3 Upload**:
   - Files are uploaded to an S3 bucket.
   - The directory structure is dynamically created based on the `TIMESTAMP_COLUMN` (year, month, day).

4. **Clean-up**:
   - Local Parquet files are deleted after a successful upload to S3.

---

## Notes
- **Error Handling**: If the S3 upload fails, the script prints an error and does not delete the local file.
- **Customizing Chunk Size**: You can change the chunk_size variable inside the script if needed.
- **Security**: Sensitive credentials should be stored in .env and not committed to version control.

---

## Directory Structure
Example output in S3:
```
s3://your-s3-bucket/developer_logs/
  year=2023/
    month=09/
      day=01/
        data-0000.parquet
        data-0001.parquet
      day=02/
        data-0002.parquet
```

---

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License
This project is licensed under the MIT License.

---

## Contact
For any issues, please contact:
- **Name:** Brandon Estrella
- **Email:** brandon@sitetransition.com