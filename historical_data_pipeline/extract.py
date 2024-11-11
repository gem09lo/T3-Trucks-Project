"""Connects to S3 bucket and downloads relevant files"""
from os import environ
from boto3 import client
from dotenv import load_dotenv


def connect_to_s3():
    """Connects to S3 using credentials from .env file"""

    s3 = client("s3", aws_access_key_id=environ["ACCESS_KEY_ID"],
                aws_secret_access_key=environ["SECRET_ACCESS_KEY"])
    return s3


def download_truck_data_files(s3, bucket_name, file_prefix, file_extension):
    """Downloads relevant files from S3 to a data/ folder."""
    bucket = s3.list_objects(Bucket=bucket_name)

    contents = bucket.get("Contents", [])
    files_needed = []

    for file in contents:
        data = file["Key"]
        if data.startswith(file_prefix) and data.endswith(file_extension):
            files_needed.append(data)

    for file in files_needed:
        s3.download_file(bucket_name,
                         file, file.split("/")[1])


def main_extract():
    """Connects to bucket and download relevant files"""
    client = connect_to_s3()

    download_truck_data_files(
        client, "sigma-resources-truck", "historical/TRUCK_DATA_HIST", ".parquet")

    download_truck_data_files(
        client, "sigma-resources-truck", "metadata/details", ".xlsx")


if __name__ == "__main__":

    load_dotenv()
    main_extract()
