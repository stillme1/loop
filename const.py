import datetime

BASE_TIME = datetime.date(2000, 1, 1)
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