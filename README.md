# loop


setup .env file in the following format:

```
# Postgres Configuration
DB_HOST=localhost
DB_NAME=postgres
DB_USER=postgres
DB_PORT=5432
DB_PASSWORD= <your_password>

# Csv paths
CSV_PATH=/home/sahil/Documents #This path is used to load the csv to db and store the report after generation
```
store 3 csv in the ```CSV_PATH```:
- business_hours.csv
- store_status.csv
- timezone.csv


Start the server:
Install and setup postgres locally
Install required python dependencies

To initialize and load the database:
```
python model/database.py
python model.loaddb.py
```

To run the service:
```
python routes.py
```


Logic for extrapolating uptime:

OptimisticUptime:
- Assume the restaurant is always open in business hour, unless we recieve an "inactive" ping.
- Iterate through all the pings in sorted order and when recieve an "inactive" ping from uptime subtract half the duration from last ping, 30 minutes, or duration from opening time (whichever is least).
- At the same time from uptime subtract half the duration to the next ping or 30 minutes or duration for closing time (whichever is least).

PessimisticUptime:
- Assume the resturant is always closed, unless we recieve an "active" ping.
- Use the exact same algorithm as above but this time in reverse, i.e. subtract from downtime when get an "active" ping.

Now during the time duration (eg, 1 week), if there are total ```x``` active pings and ```y``` inactive pings. (Only during restaurants' business hours)
We define ```fraction``` as ```x / (x+y)```

``` uptime = fraction * optimisticUptime + (1-fraction) * pessimisticUptime ```

Note: For last hour uptime, we use exact same algorithm, except we calculate fraction for last 3 hours.
