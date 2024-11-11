


# Tasty Truck Treats (T3) Data Pipeline Project
## Overview
Tasty Truck Treats (T3) is a dynamic catering company specializing in operating a fleet of food trucks around Lichfield. With each truck offering a unique menu, T3 provides a wide range of culinary experiences to its customers. This project focuses on building an automated ETL (Extract, Transform, Load) pipeline to gather and analyze transaction-level data from all food trucks. The insights obtained will be used to refine menu offerings, improve marketing strategies, and optimize overall fleet management.

## Project Objectives
- Develop an ETL pipeline that collects transaction data from T3 trucks.
- Build a dashboard for live data visualization and generate regular summary reports.
- Enable stakeholders to make informed decisions based on real-time data insights.

## Stakeholders
- **Hiram Boulie (CFO):** Focused on cutting costs and raising profits. Requires robust financial data for company stability and acquisition talks.
- **Miranda Courcelle (Head of Culinary Experience):** Interested in understanding customer preferences across locations to optimize menus and pricing.



## 🛠️ Getting Setup

1. **AWS credentials** Ensure you have a `.env` file with your AWS credentials (ACCESS_KEY_ID, SECRET_ACCESS_KEY) and credentials for Redshift Database.
2. Install Requirements:
- **Docker**:
   - Install Docker to run the application in a containerized environment.
- **Dependencies**:
   - Install necessary packages: `pip install -r requirements.txt`.
3. **Database Setup** 
- [x]


## 🗂️ Files Explained

- `README.md`
  - This is the file you are currently reading
- `.gitignore`
  - This file is used to tell Git what files to ignore for any changes. This can be safely ignored.
- `extract.py`
  - Extracts raw transaction data from an S3 bucket and stores it locally.
  - Performs file filtering to download only relevant .parquet and metadata files.
- `transform.py`:
  - Processes the downloaded data by combining it into a single CSV file.
  - Cleans the data by removing invalid transactions and prepares it for loading into the database.
- `load.py`:
  - Establishes a connection to the Redshift database.
  - Inserts the cleaned transaction data into the fact and dimension tables to maintain data integrity and association.
- `etl.py`:
  - The main orchestrator script that runs the entire ETL process sequentially.
- `schema.sql`:
  - Contains SQL commands for creating and seeding tables in the Redshift database, establishing the necessary STAR schema.
- `Dockerfile`:
  - Defines the environment where the ETL application will run, including all dependencies and necessary scripts.

**Data modelling - Star Schema**
![alt text](image.png)