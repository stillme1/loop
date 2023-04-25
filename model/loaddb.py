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

# Truncate the tables
cur.execute("TRUNCATE TABLE store_status;")
cur.execute("TRUNCATE TABLE business_hours;")
cur.execute("TRUNCATE TABLE timezone;")

# Define the file paths of the CSV files to load
store_status_csv = os.getenv("CSV_PATH") + "/store_status.csv"
business_hours_csv = os.getenv("CSV_PATH") + "/business_hours.csv"
timezone_csv = os.getenv("CSV_PATH") + "/timezone.csv"
store_csv = os.getenv("CSV_PATH") + "/store_status.csv"

# Define the SQL statement to load the store_status CSV file into the table
load_store_status_query = '''COPY store_status(store_id, status, timestamp_utc)
                                FROM '{}'
                                DELIMITER ','
                                CSV HEADER;'''.format(store_status_csv)

# Define the SQL statement to load the business_hours CSV file into the table
load_business_hours_query = '''COPY business_hours(store_id, day, start_time_local, end_time_local) 
                               FROM '{}' 
                               DELIMITER ',' 
                               CSV HEADER;'''.format(business_hours_csv)

# Define the SQL statement to load the timezone CSV file into the table
load_timezone_query = '''COPY timezone(store_id, timezone_str) 
                         FROM '{}' 
                         DELIMITER ',' 
                         CSV HEADER;'''.format(timezone_csv)

# create temp table to store store_id
create_temp_table_query = '''CREATE TABLE store AS
                                SELECT DISTINCT store_id
                                FROM store_status;'''



# Execute the SQL statements to load the CSV files into the tables
cur.execute(load_store_status_query)
cur.execute(load_business_hours_query)
cur.execute(load_timezone_query)
cur.execute(create_temp_table_query)

# Commit the changes to the database
conn.commit()

# Close the cursor and the connection
cur.close()
conn.close()
