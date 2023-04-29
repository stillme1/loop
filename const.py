import datetime
import os

from dotenv import load_dotenv
load_dotenv()

# BASE date time of 2023-01-25 18:13:22.47922
BASE_DATETIME = datetime.datetime(2023, 1, 25, 18, 13, 22, 479220)

# max delta of 7 days and 1 hour
ONE_WEEK = datetime.timedelta(days=7, hours=0)
ONE_DAY = datetime.timedelta(days=1, hours=0)
ONE_HOUR = datetime.timedelta(days=0, hours=1)
THREE_HOURS = datetime.timedelta(days=0, hours=3)
BASE_DATE = datetime.date(2000, 1, 1)
EOD = datetime.time(23, 59, 59)
BOD = datetime.time(0, 0, 0)
DEFAULT_TIMEZONE = 'America/Chicago'
DEFAULT_BUSINESS_HOURS = [
    [0, BOD, EOD],
    [1, BOD, EOD],
    [2, BOD, EOD],
    [3, BOD, EOD],
    [4, BOD, EOD],
    [5, BOD, EOD],
    [6, BOD, EOD]
]

ROOTPATH = os.getenv("CSV_PATH")

