import os
from dotenv import load_dotenv
import psycopg2
from datetime import datetime, timedelta, timezone
import pytz
import const as const


def getBusinessHoursInUCT(store_id, cur):
    # Get the timezone for the store
    get_timezone_query = f"SELECT timezone_str FROM timezone WHERE store_id = {store_id}"
    cur.execute(get_timezone_query)
    
    timezone_str = const.DEFAULT_TIMEZONE if cur.rowcount==0 else cur.fetchone()[0]
    timezone_obj = pytz.timezone(timezone_str)
    delta = timezone_obj.utcoffset(datetime.now())

    # print(delta)

    # Get the business hours for the store
    get_business_hours_query = f"SELECT * FROM business_hours WHERE store_id = {store_id}"
    cur.execute(get_business_hours_query)
    

    uct_time = const.DEFAULT_BUSINESS_HOURS if cur.rowcount==0 else []
    for row in cur:
        localStartTime = datetime.combine(const.BASE_TIME, row[2])
        localEndTime = datetime.combine(const.BASE_TIME, row[3])
        
        utcStartTime = localStartTime - delta
        utcEndTime = localEndTime - delta
        
        day1 = 0
        day2 = 0
        if(utcStartTime.day != localStartTime.day):
            day1 = -1 if delta.days==0 else 1
        if(utcEndTime.day != localEndTime.day):
            day2 = -1 if delta.days==0 else 1
        
        day1 = (day1 + row[1] + 7) % 7
        day2 = (day2 + row[1] + 7) % 7

        if(day1 == day2):
            uct_time.append([day1, utcStartTime.time(), utcEndTime.time()])
        else:
            uct_time.append([day1, utcStartTime.time(), const.EOD])
            uct_time.append([day2, const.BOD, utcEndTime.time()])

    return sorted(uct_time, key=lambda x: (x[0], x[1]))




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

# get first 100 store_id
get_store_id_query = "SELECT store_id FROM store LIMIT 14092"
cur.execute(get_store_id_query)

rows = cur.fetchall()
for row in rows:
    store_id = row[0]
    x = getBusinessHoursInUCT(store_id, cur)
    print(f"Store {store_id} business hours in UTC:")
    for i in x:
        print(i)