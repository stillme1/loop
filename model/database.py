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
conn.commit()

# Define the SQL statement to create a table with the desired columns and primary key
create_store_status = '''CREATE TABLE store_status (
                            store_id BIGINT,
                            timestamp_utc TIMESTAMP WITH TIME ZONE,
                            status CHAR(8) NOT NULL,
                            PRIMARY KEY (store_id, timestamp_utc),
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


# Execute the SQL statement to create the table
cur.execute(create_store_status)
cur.execute(create_business_hours)
cur.execute(create_timezone)
conn.commit()
cur.close()
conn.close()
