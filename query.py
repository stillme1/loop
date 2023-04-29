import datetime
import os
from dotenv import load_dotenv
import psycopg2
import pytz

import const as const


load_dotenv()
# Connect to PostgreSQL database
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT"),
)

get_store_id_query = "SELECT s.store_id, t.timezone_str, bh.day, bh.start_time_local, bh.end_time_local \
                    FROM store s \
                    LEFT OUTER JOIN timezone t ON s.store_id = t.store_id \
                    LEFT OUTER JOIN business_hours bh ON s.store_id = bh.store_id \
                    ORDER BY s.store_id \
                    "

cluser_query = "CLUSTER store_status USING store_id_idx;"

get_pollData_query = "SELECT timestamp_utc, status FROM store_status WHERE \
                    timestamp_utc > %s \
                    AND timestamp_utc <= %s \
                    AND store_id = %s"

add_report_query = "INSERT INTO report (report_id, status) VALUES (DEFAULT, %s) RETURNING report_id;"

update_report_query = "UPDATE report SET status = %s WHERE report_id = %s;"

get_report_status_query = "SELECT status FROM report WHERE report_id = %s;"

def clusterStoreStatus():
    cur = conn.cursor()
    cur.execute(cluser_query)
    conn.commit()

def addReport(status):
    cur = conn.cursor()
    cur.execute(add_report_query, (status,))
    conn.commit()
    return cur.fetchone()[0]

def updateReport(status, report_id):
    cur = conn.cursor()
    cur.execute(update_report_query, (status, report_id))
    conn.commit()

def getReportStatus(report_id):
    cur = conn.cursor()
    cur.execute(get_report_status_query, (report_id,))
    row = cur.fetchall()
    if len(row) == 0:
        return "Report not found"
    return row[0][0]


def getBusinessHoursInUTC(timezone_str, business_hours):
    if timezone_str is None:
        timezone_str = const.DEFAULT_TIMEZONE
    if business_hours[0][1] is None:
        return const.DEFAULT_BUSINESS_HOURS

    timezone_obj = pytz.timezone(timezone_str)
    delta = timezone_obj.utcoffset(datetime.datetime.now())

    uct_time = []
    for row in business_hours:
        localStartTime = datetime.datetime.combine(const.BASE_DATE, row[1])
        localEndTime = datetime.datetime.combine(const.BASE_DATE, row[2])
        
        utcStartTime = localStartTime - delta
        utcEndTime = localEndTime - delta
        
        day1 = 0
        day2 = 0
        if(utcStartTime.day != localStartTime.day):
            day1 = -1 if delta.days==0 else 1
        if(utcEndTime.day != localEndTime.day):
            day2 = -1 if delta.days==0 else 1
        
        day1 = (day1 + row[0] + 7) % 7
        day2 = (day2 + row[0] + 7) % 7

        if(day1 == day2):
            uct_time.append([day1, utcStartTime.time(), utcEndTime.time()])
        else:
            uct_time.append([day1, utcStartTime.time(), const.EOD])
            uct_time.append([day2, const.BOD, utcEndTime.time()])

    return sorted(uct_time, key=lambda x: (x[0], x[1]))


def getStoreIdWithBusinessHours():
    cur = conn.cursor()
    cur.execute(get_store_id_query)
    rows = cur.fetchall()

    storeWithBusinessHours = []
    store_id = 0
    business_hours = []

    for row in rows:
        if row[0] == store_id:
            business_hours.append(row[2:])
        elif store_id == 0:
            store_id = row[0]
            business_hours.append(row[2:])
        else:
            x = getBusinessHoursInUTC(row[1], business_hours)
            storeWithBusinessHours.append((store_id, x))
            business_hours = []
            store_id = row[0]
            business_hours.append(row[2:])
    x = getBusinessHoursInUTC(rows[len(row)-1][1], business_hours)
    storeWithBusinessHours.append((store_id, x))

    return sorted(storeWithBusinessHours, key=lambda x: x[0])

def getPollData(startTime, endTime, store_id):
    cur = conn.cursor()
    params = (startTime, endTime, store_id)
    cur.execute(get_pollData_query, params)
    rows = cur.fetchall()
    return sorted(rows, key=lambda x: x[0])


# startTime: datetime.datetime
# endTime: datetime.datetime
# businessHours: [[weekday, datetime.time, datetime.time]]
def getBusinessMinutesBetweenTwoTime(startTime, endTime, businessHours):
    totalTime = 0
    currDate = startTime.date()
    while currDate <= endTime.date():
        for day in businessHours:
            if day[0] == currDate.weekday():
                totalTime += (day[2].hour - day[1].hour) * 60 + (day[2].minute - day[1].minute) + (day[2].second - day[1].second) / 60
        currDate += datetime.timedelta(days=1)
    # subtract business hours of startTime.BOD to startTime.time() and endTime.time() to endTime.EOD
    for day in businessHours:
        if day[0] == startTime.weekday():
            if(day[1] >= startTime.time()):
                continue
            else:
                extra = (min(day[2], startTime.time()).hour - day[1].hour) * 60 + (min(day[2], startTime.time()).minute - day[1].minute) + (min(day[2], startTime.time()).second - day[1].second) / 60
                totalTime -= extra

    for day in businessHours:
        if day[0] == endTime.weekday():
            if(day[2] < endTime.time()):
                continue
            else:
                extra = (day[2].hour - max(day[1], endTime.time()).hour) * 60 + (day[2].minute - max(day[1], endTime.time()).minute) + (day[2].second - max(day[1], endTime.time()).second) / 60
                totalTime -= extra
    return round(totalTime)


def isBusinessHour(timestamp, businessHour):
    for days in businessHour:
        if(days[0] != timestamp.weekday()):
            continue
        if(days[1] <= timestamp.time() and days[2] >= timestamp.time()):
            return True, round((timestamp - datetime.datetime.combine(timestamp.date(), days[1])).total_seconds() / 60) \
                    , round((datetime.datetime.combine(timestamp.date(), days[2]) - timestamp).total_seconds() / 60)
    return False, 0, 0