"""Streamlit Dashboard"""
import streamlit as st
import pandas as pd
import altair as alt
from os import environ
import redshift_connector
from dotenv import load_dotenv


def connect_to_redshift():
    """Establish a connection to Redshift"""
    load_dotenv()

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


def get_data(cursor):
    """Gets all the data from the Redshift Database"""
    cursor.execute("SET search_path TO gem_lo_schema;")
    cursor.execute("SELECT * FROM fact_transaction;")
    data = cursor.fetchall()

    columns = ["transaction_id", "timestamp", "total", "type", "truck_id"]

    df = pd.DataFrame(data, columns=columns)
    print(df.head())
    return df


def main_title():
    """Homepage title and overview"""
    st.title("Dashboard - Chief Financial Officer")
    st.write("""Tasty Truck Treats (T3) is a catering company that specializes in 
            operating a fleet of food trucks in Lichfield and its surrounding areas.""")
    st.write("""This dashboard helps the CFO to ensure that the company is on track to 
            be both stable and profitable over the next five years. """)
    st.write("""Priorities: Cut Costs and Raise Profits """)


def load_data():
    """Loads the data to dataframe"""
    data = pd.read_csv("cleaned_truck_data.csv")
    return data


def filter_by_truck(df):
    """A filter for truck selection"""
    truck_list = df["truck_id"].unique()
    selected_trucks = st.multiselect(
        "Select Trucks to Filter:",
        truck_list,
        key="Filter by Truck"
    )
    return selected_trucks


def filter_by_date(df):
    """A filter for date selection"""

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    unique_dates = sorted(df['timestamp'].dt.date.unique())

    selected_date = st.selectbox(
        "Select Date:", unique_dates, key="Filter by Date")
    return selected_date


def total_transactions_count(df, selected_trucks):
    """Displays bar chart of total number of transactions filtered by trucks"""

    filtered_trucks = df["truck_id"].isin(selected_trucks)
    counts = df[filtered_trucks]["truck_id"].value_counts().reset_index()
    counts.columns = ["truck_id", "count"]

    chart = alt.Chart(counts, title="Total Number of Transactions Per Trucks").mark_bar().encode(
        x=alt.X("truck_id:O", title="Truck ID"),
        y=alt.Y("count:Q", title="Number of Transactions"),
        color="truck_id:N")

    st.altair_chart(chart, use_container_width=True)


def total_revenue_query(cursor):
    """SQL query for calculating total revenue"""
    cursor.execute("SET search_path TO gem_lo_schema;")
    cursor.execute("""SELECT truck_id, SUM(total) as total_revenue
            FROM fact_transaction
            GROUP BY truck_id;""")

    data = cursor.fetchall()
    print(data)

    columns = ["truck_id", "total_revenue"]
    revenue_df = pd.DataFrame(data, columns=columns)
    print(revenue_df)

    return revenue_df


def total_revenue(cursor, selected_trucks):
    """Shows bar chart of total revenue filtered by truck"""

    revenue_df = total_revenue_query(cursor)
    filtered_trucks = revenue_df[revenue_df["truck_id"].isin(selected_trucks)]
    print(filtered_trucks)

    chart = alt.Chart(filtered_trucks).mark_bar().encode(
        x=alt.X("truck_id:O", title="Truck ID"),
        y=alt.Y("total_revenue:Q", title="Total Revenue (£)"),
        color="truck_id:N"
    ).properties(
        title="Total Revenue for Each Truck"
    )

    st.altair_chart(chart, use_container_width=True)


def average_transaction_value(df, selected_trucks, selected_date):
    """Creates a line graph of average transaction value"""

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    filtered_df = df[
        (df['truck_id'].isin(selected_trucks)) &
        (df['timestamp'].dt.date == selected_date)
    ]

    filtered_df['hour'] = filtered_df['timestamp'].dt.hour

    avg_transaction_per_truck = filtered_df.groupby(
        ["truck_id", "hour"])["total"].mean().reset_index()

    st.write("## Average Transaction Value Over Time")
    chart = alt.Chart(avg_transaction_per_truck).mark_line(point=True).encode(
        x=alt.X("hour:O", title="Hour of Day"),
        y=alt.Y("total:Q", title="Average Transaction Value (£)"),
        color="truck_id:N"
    ).properties(
        title=f"Average Transaction Value on {selected_date}"
    )

    st.altair_chart(chart, use_container_width=True)


def total_transactions_payment_type(df, selected_trucks):
    """Pie chart displaying number of transactions by card and cash"""

    filtered_trucks = df["truck_id"].isin(selected_trucks)

    transaction_by_payment = df[filtered_trucks].groupby(
        "type")["total"].count().reset_index()
    transaction_by_payment.columns = ["payment_type", "transaction_count"]

    chart = alt.Chart(transaction_by_payment).mark_arc().encode(
        theta=alt.Theta("transaction_count:Q"),
        color=alt.Color("payment_type:N", title="Payment Type")).properties(
        title="Transaction Volume by Payment Type")

    st.altair_chart(chart, use_container_width=True)


def main():
    """Main function"""
    main_title()

    connection = connect_to_redshift()
    cursor = get_cursor(connection)

    df = get_data(cursor)

    selected_trucks = filter_by_truck(df)
    selected_date = filter_by_date(df)

    col1, col2 = st.columns(2)

    with col1:
        total_revenue(cursor, selected_trucks)
    with col2:
        total_transactions_payment_type(df, selected_trucks)

    average_transaction_value(df, selected_trucks, selected_date)

    connection.close()
    cursor.close()


if __name__ == "__main__":
    main()
