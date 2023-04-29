import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
# Connect to PostgreSQL database
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT"),
)

# Create a cursor object
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS store_status;")
cur.execute("DROP TABLE IF EXISTS business_hours;")
cur.execute("DROP TABLE IF EXISTS timezone;")
cur.execute("DROP TABLE IF EXISTS report;")
conn.commit()

# Define the SQL statement to create a table with the desired columns and primary key
create_store_status = '''CREATE TABLE store_status (
                            store_id BIGINT,
                            timestamp_utc TIMESTAMP,
                            status CHAR(8) NOT NULL,
                            CHECK (store_id > 0)
                        );'''

create_business_hours = '''CREATE TABLE business_hours (
                            store_id BIGINT,
                            day INT,
                            start_time_local TIME,
                            end_time_local TIME,
                            PRIMARY KEY (store_id, day, start_time_local, end_time_local),
                            CHECK (store_id > 0)
                        );'''

create_timezone =       '''CREATE TABLE timezone (
                            store_id BIGINT,
                            timezone_str VARCHAR(50) NOT NULL,
                            PRIMARY KEY (store_id),
                            CHECK (store_id > 0)
                        );'''
create_index_query = '''CREATE INDEX store_id_idx ON store_status (store_id);'''

create_report_query = '''CREATE TABLE report (
                            report_id SERIAL,
                            status VARCHAR(10) NOT NULL
                        );'''

# Execute the SQL statement to create the table
cur.execute(create_store_status)
cur.execute(create_business_hours)
cur.execute(create_timezone)
cur.execute(create_report_query)
cur.execute(create_index_query)
conn.commit()
cur.close()
conn.close()
