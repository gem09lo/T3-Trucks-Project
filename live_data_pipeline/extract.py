"""Imports"""
from os import environ
from datetime import datetime
from boto3 import client
from dotenv import load_dotenv


def connect_to_s3():
    """Connects to S3 using credentials from .env file"""

    s3 = client("s3", aws_access_key_id=environ["ACCESS_KEY_ID"],
                aws_secret_access_key=environ["SECRET_ACCESS_KEY"])
    return s3


def download_truck_data_files(s3, bucket_name, folder_prefix, file_prefix, file_extension):
    """Downloads relevant files from S3 to a data/folder."""
    folder_path = f"trucks/{folder_prefix}/{file_prefix}"
    print(folder_path)

    bucket = s3.list_objects(Bucket=bucket_name)

    contents = bucket.get("Contents", [])
    files_needed = []
    print(files_needed)

    for file in contents:
        data = file["Key"]
        if data.startswith(folder_path) and data.endswith(file_extension):
            files_needed.append(data)

    if files_needed:
        for file in files_needed:
            s3.download_file(bucket_name,
                             file, file.split("/")[-1])
            print(f"{file} downloaded successfully")
    else:
        print("No data was uploaded")

# Above and beyond


def download_truck_metadata(s3, bucket_name, folder_prefix, file_prefix, file_extension):
    """Downloads metadata from S3 to a data/folder."""
    folder_path = f"{folder_prefix}/{file_prefix}"
    print(folder_path)

    bucket = s3.list_objects(Bucket=bucket_name)

    contents = bucket.get("Contents", [])
    files_needed = []

    for file in contents:
        data = file["Key"]
        if data.startswith(folder_path) and data.endswith(file_extension):
            files_needed.append(data)
    print(files_needed)

    if files_needed:
        for file in files_needed:
            s3.download_file(bucket_name,
                             file, file.split("/")[-1])
            print(f"{file} downloaded successfully")
    else:
        print("No data was uploaded")


def get_current_datetime() -> datetime:
    """Returns current datetime"""
    batch_hours = [12, 15, 18, 21]

    current_day = datetime.now().day
    current_month = datetime.now().month
    current_year = datetime.now().year

    current_hour = datetime.now().hour

    if current_hour < 12:
        print("No data to upload")
        return None
    last_batch_hour = max(hour for hour in batch_hours if current_hour >= hour)
    return f"{current_year}-{current_month}/{current_day}/{last_batch_hour}"


def main_extract():
    """Connects to bucket and download relevant files"""

    bucket = "sigma-resources-truck"

    client = connect_to_s3()

    current_date_filepath = get_current_datetime()

    download_truck_data_files(
        client, bucket, current_date_filepath, "T3_T", ".csv")


# uploads at 12/15/18/21 each day
if __name__ == "__main__":

    load_dotenv()

    main_extract()
