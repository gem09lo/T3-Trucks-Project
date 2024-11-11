"""Connects to Redshift database and uploads data to it"""
from os import environ
import redshift_connector
from dotenv import load_dotenv
import pandas as pd


def connect_to_redshift():
    """Establish a connection to Redshift"""
    conn = redshift_connector.connect(
        user=environ["DATABASE_USERNAME"],
        password=environ["DATABASE_PASSWORD"],
        host=environ["DATABASE_HOST"],
        port=environ["DATABASE_PORT"],
        database=environ["DATABASE_NAME"]
    )
    return conn


def get_cursor(conn) -> redshift_connector.Cursor:
    """Returns cursor"""
    return conn.cursor()


def get_sample_data() -> pd.DataFrame:
    """Returns sample data from the truck csv file"""
    return pd.read_csv("./cleaned_truck_data.csv").sample(3000)


def insert_into_database(conn, cur, data: list) -> None:
    """Inserting sample truck data into transaction table"""
    cur.executemany(
        """INSERT INTO FACT_Transaction (at, payment_method_id, total, truck_id)
        VALUES (%s, %s, %s, %s)""", (data))
    conn.commit()


def upload_transaction_data():
    """Uploads transaction data to the database."""
    connection = connect_to_redshift()
    cursor = get_cursor(connection)

    cursor.execute("SET search_path TO gem_lo_schema;")

    sample = get_sample_data()

    formatted_sample = sample.values.tolist()

    insert_into_database(connection, cursor, formatted_sample)

    print("Uploaded successfully")
    connection.close()


if __name__ == "__main__":

    load_dotenv()

    upload_transaction_data()
