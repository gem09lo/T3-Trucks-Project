"""Connects to the redshift database and analyses data"""
import json
import os
from datetime import datetime
from os import environ
import redshift_connector
from dotenv import load_dotenv


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


def get_transaction_value_all_trucks(cursor):
    """Returns the total transaction value across all trucks"""
    cursor.execute(
        """SELECT ROUND(SUM(total), 2) as TOTAL_TRANSACTION_VALUE
           FROM fact_transaction
           WHERE at::DATE = DATEADD(day, -1, CURRENT_DATE);"""
    )
    return cursor.fetchone()[0]


def get_transaction_value_and_count(cursor):
    """Returns the total transaction value and count for each truck"""
    cursor.execute(
        """SELECT truck_id, ROUND(SUM(total), 2) as TOTAL_TRANSACTION_VALUE, COUNT(total) as COUNT_TRANSACTIONS
           FROM fact_transaction 
           WHERE at::DATE = DATEADD(day, -1, CURRENT_DATE)
           GROUP BY truck_id;"""
    )
    return cursor.fetchall()


def create_report_data(total_value, transactions_by_truck):
    """returns query output into a dictionary format"""

    report_data = {
        "summary": {
            "total_transaction_value": total_value,
            "transactions_by_truck": []
        }
    }

    for row in transactions_by_truck:
        truck_data = {
            "truck_id": row[0],
            "total_transaction_value": row[1],
            "count_transactions": row[2]
        }
        report_data["summary"]["transactions_by_truck"].append(truck_data)

    return report_data


def save_to_json(report_data):
    """Saves the report data to a json file"""
    report_directory = "report_data"
    os.makedirs(report_directory, exist_ok=True)

    date = datetime.now().strftime('%Y-%m-%d')
    output_file = os.path.join(report_directory, f"report_data_{date}.json")

    with open(output_file, "w") as json_file:
        json.dump(report_data, json_file, indent=2)

    print(f"Data saved to {output_file} successfully.")


def save_to_html(report_data):
    """Saves the report data to a html file"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Transaction Summary Report</title>
        <style>
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 8px;
                border: 1px solid #ddd;
                text-align: center;
            }}
            th {{
                background-color: #F2F2F2;
            }}
        </style>
    </head>
    <body>
        <h1>Transaction Summary Report</h1>
        <h2>Total Transaction Value: £{report_data['summary']['total_transaction_value']:.2f}</h2>
        <table>
            <thead>
                <tr>
                    <th>Truck ID</th>
                    <th>Total Transaction Value</th>
                    <th>Count of Transactions</th>
                </tr>
            </thead>
            <tbody>
    """

    for transaction in report_data['summary']['transactions_by_truck']:

        html_content += f"""
            <tr>
                <td>{transaction['truck_id']}</td>
                <td>£{transaction['total_transaction_value']:.2f}</td>
                <td>{transaction['count_transactions']}</td>
            </tr>
        """

    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    return html_content


def lambda_handler(event, context):
    """Fetches transaction data and saves it to a JSON file"""
    connection = connect_to_redshift()
    cursor = get_cursor(connection)

    try:
        cursor.execute("SET search_path TO gem_lo_schema;")
        total_value_all_trucks = get_transaction_value_all_trucks(cursor)
        value_and_count_per_truck = get_transaction_value_and_count(cursor)

        report_data = create_report_data(
            total_value_all_trucks, value_and_count_per_truck)

    finally:
        connection.close()

    return {
        'statusCode': 200,
        'body': save_to_html(report_data)
    }


if __name__ == "__main__":

    load_dotenv()
    lambda_handler()
