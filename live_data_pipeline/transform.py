"""Cleans data downloaded from S3 bucket"""
import os
import pandas as pd


def clean_data(csv_file: str, output_file: str):
    """Cleans the data in given CSV file"""

    truck_data = pd.read_csv(csv_file)

    truck_data["total"] = pd.to_numeric(truck_data["total"], errors="coerce")
    truck_data.dropna(subset=["total"], inplace=True)
    truck_data = truck_data[truck_data["total"] != 0.0]
    truck_data = truck_data[(truck_data["total"] > 0.0)
                            & (truck_data["total"] < 20.0)]

    payment_type = {"card": "1", "cash": "2"}
    truck_data["type"] = pd.to_numeric(
        truck_data["type"].replace(payment_type))

    truck_id = get_truck_id(csv_file)
    truck_data["truck_id"] = int(truck_id)

    truck_data["timestamp"] = pd.to_datetime(truck_data["timestamp"])

    truck_data = truck_data.dropna()

    truck_data.to_csv(output_file, index=False)
    (print(f"{csv_file} cleaned successfully"))

    os.remove(csv_file)
    return truck_data


# def remove_files():
#     """Removes downloaded files"""
#     os.remove()


def get_truck_id(csv_file: str):
    """returns the truck id that the data belongs to"""
    return int(csv_file.split("_")[1][1])


def combine_truck_data_files():
    """Combines all cleaned truck data files into a single CSV file."""
    all_data = []
    folder_path = "./"

    for file in os.listdir(folder_path):
        if file.startswith("cleaned_T3") and file.endswith(".csv"):
            file_path = os.path.join(folder_path, file)

            data = pd.read_csv(file_path)
            all_data.append(data)

            os.remove(file_path)

    combined_data = pd.concat(all_data, ignore_index=True)
    combined_data.to_csv("combined_cleaned_truck_data.csv", index=False)
    print("Combined cleaned truck_data successfully")


def main_transform():
    """Main function for cleaning and combining the truck data."""
    truck_csv_files = [file for file in os.listdir(
        "./") if file.startswith("T3_") and file.endswith(".csv")]

    for truck_csv in truck_csv_files:
        cleaned_csv = f"cleaned_{truck_csv}"
        clean_data(truck_csv, cleaned_csv)

    combine_truck_data_files()


if __name__ == "__main__":

    main_transform()
