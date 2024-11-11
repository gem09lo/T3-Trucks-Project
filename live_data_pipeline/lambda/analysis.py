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


def save_report_to_json(total_value, transactions_by_truck):
    """Saves the report data to a JSON file"""

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

    get_html_contents(report_data)
    # report_directory = "report_data"
    # os.makedirs(report_directory, exist_ok=True)

    # date = datetime.now().strftime('%Y-%m-%d')
    # # output_file = os.path.join(report_directory, f"report_data_{date}.json")

    # # with open(output_file, "w") as json_file:
    # #     json.dump(report_data, json_file, indent=2)

    # print(f"Data saved to {output_file} successfully.")


def get_html_contents(report_data):
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

    # Add rows for each truck transaction data
    for transaction in report_data['summary']['transactions_by_truck']:

        html_content += f"""
            <tr>
                <td>{transaction['truck_id']}</td>
                <td>£{transaction['total_transaction_value']:.2f}</td>
                <td>{transaction['count_transactions']}</td>
            </tr>
        """

    # Closing the table and HTML structure
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    # Write to an HTML file
    with open("transaction_summary_report.html", "w") as file:
        file.write(html_content)
    print("HTML report generated as 'transaction_summary_report.html'")


def get_transaction_data():
    """Fetches transaction data and saves it to a JSON file"""
    connection = connect_to_redshift()
    cursor = get_cursor(connection)

    try:
        cursor.execute("SET search_path TO gem_lo_schema;")
        total_value_all_trucks = get_transaction_value_all_trucks(cursor)
        value_and_count_per_truck = get_transaction_value_and_count(cursor)

        save_report_to_json(total_value_all_trucks, value_and_count_per_truck)

    finally:
        connection.close()


if __name__ == "__main__":

    load_dotenv()
    get_transaction_data()
