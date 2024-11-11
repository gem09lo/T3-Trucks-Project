"""Complete ETL pipeline"""
from dotenv import load_dotenv
from extract import main_extract
from transform import main_transform
from load import upload_transaction_data


def run_etl_pipeline():
    """Downloads, cleans and processes the data then uploads it to Redshift database"""
    load_dotenv()

    main_extract()
    main_transform()
    upload_transaction_data()


if __name__ == "__main__":

    run_etl_pipeline()
