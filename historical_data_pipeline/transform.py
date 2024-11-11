"""Combines data into CSV and cleans it"""
import os
import pandas as pd


def combine_transaction_data_files():
    """Loads and combines relevant files from the data/ folder.

    Produces a single combined file in the data/ folder."""

    all_data = []
    folder_path = "./"

    for file in os.listdir(folder_path):
        if file.startswith("TRUCK_DATA") and file.endswith(".parquet"):
            file_path = os.path.join(folder_path, file)

            data = pd.read_parquet(file_path)

            truck_id = int(file.split('_')[-1].split(".")[0])
            data['truck_id'] = truck_id

            all_data.append(data)

            os.remove(file_path)

    combined_data = pd.concat(all_data, ignore_index=True)

    combined_data.to_csv("combined_truck_data.csv", index=False)


def clean_data(csv_file: str, output_file: str):
    """Cleans the data in given CSV file"""

    truck_data = pd.read_csv(csv_file)

    truck_data["total"] = pd.to_numeric(truck_data["total"], errors="coerce")

    truck_data.dropna(subset=["total"], inplace=True)
    truck_data = truck_data[truck_data["total"] != 0.0]

    payment_type = {"card": "1", "cash": "2"}
    truck_data["timestamp"] = pd.to_datetime(truck_data["timestamp"])
    truck_data["type"] = pd.to_numeric(
        truck_data["type"].replace(payment_type))
    truck_data["truck_id"] = pd.to_numeric(truck_data["truck_id"])

    truck_data = truck_data.dropna()

    truck_data.to_csv(output_file, index=False)

    os.remove(csv_file)
    return truck_data


def remove_files():
    """Removes downloaded files"""
    os.remove()


def main_transform():
    """Main function for combining and cleaning the data"""
    truck_csv = "combined_truck_data.csv"
    cleaned_csv = "cleaned_truck_data.csv"

    combine_transaction_data_files()
    clean_data(truck_csv, cleaned_csv)


if __name__ == "__main__":

    main_transform()
