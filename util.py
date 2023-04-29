import csv
import datetime

import const as const
import query as query


def optimisticDowntime(startTime, endTime, pollData, businessHours):
    downtime = 0
    lastPollTime = startTime
    up = 0
    down = 0
    
    for i in range(len(pollData)):
        if pollData[i][0] < startTime:
            continue
        active, sinceOpen, untilClose = query.isBusinessHour(pollData[i][0], businessHours)
        if pollData[i][1] == 'active  ' and active:
            up += 1
        elif pollData[i][1] == 'inactive' and active:
            down += 1
        
        if (not active) or pollData[i][1] == 'active  ':
            lastPollTime = pollData[i][0]
            continue
        dt = min(60, (pollData[i][0] - lastPollTime).total_seconds() / 60) / 2
        dt = min(dt, sinceOpen)
        downtime += dt

        lastPollTime = pollData[i][0]

        if i < len(pollData) - 1:
            dt = min(60, (pollData[i+1][0] - pollData[i][0]).total_seconds() / 60) / 2
            dt = min(dt, untilClose)
            downtime += dt
        else:
            dt = min(60, (endTime - pollData[i][0]).total_seconds() / 60) / 2
            dt = min(dt, untilClose)
            downtime += dt
    return downtime, 1 if (up + down == 0) else up/(up+down)

def pessimisticUptime(startTime, endTime, pollData, businessHours):
    uptime = 0

    lastPollTime = startTime

    for i in range(len(pollData)):
        if pollData[i][0] < startTime:
            continue
        active, sinceOpen, untilClose = query.isBusinessHour(pollData[i][0], businessHours)
        if (not active) or pollData[i][1] == 'inactive':
            lastPollTime = pollData[i][0]
            continue
        dt = min(120, (pollData[i][0] - lastPollTime).total_seconds() / 60) / 2
        dt = min(dt, sinceOpen)
        uptime += dt

        lastPollTime = pollData[i][0]

        if i < len(pollData) - 1:
            dt = min(120, (pollData[i+1][0] - pollData[i][0]).total_seconds() / 60) / 2
            dt = min(dt, untilClose)
            uptime += dt
        else:
            dt = min(120, (endTime - pollData[i][0]).total_seconds() / 60) / 2
            dt = min(dt, untilClose)
            uptime += dt
        
    return uptime


def lastWeekUptimeAndDowntime(pollData, businessHours):
    totalBusinessMinutes = query.getBusinessMinutesBetweenTwoTime(const.BASE_DATETIME - const.ONE_WEEK, const.BASE_DATETIME, businessHours)
    lowDowntime, fraction = optimisticDowntime(const.BASE_DATETIME - const.ONE_WEEK, const.BASE_DATETIME, pollData, businessHours)
    lowUpTime = pessimisticUptime(const.BASE_DATETIME - const.ONE_WEEK, const.BASE_DATETIME, pollData, businessHours)

    highUptime = totalBusinessMinutes - lowDowntime

    uptime = highUptime * fraction + (1-fraction) * lowUpTime
    downTime = totalBusinessMinutes - uptime
    return uptime/60, downTime/60

def lastDayUptimeAndDowntime(pollData, businessHours):
    totalBusinessMinutes = query.getBusinessMinutesBetweenTwoTime(const.BASE_DATETIME - const.ONE_DAY, const.BASE_DATETIME, businessHours)
    lowDowntime, fraction = optimisticDowntime(const.BASE_DATETIME - const.ONE_DAY, const.BASE_DATETIME, pollData, businessHours)
    lowUpTime = pessimisticUptime(const.BASE_DATETIME - const.ONE_DAY, const.BASE_DATETIME, pollData, businessHours)

    highUptime = totalBusinessMinutes - lowDowntime

    uptime = highUptime * fraction + (1-fraction) * lowUpTime
    downTime = totalBusinessMinutes - uptime
    return uptime/60, downTime/60

def lastHourUptime(pollData, businessHours):
    totalBusinessMinutes = query.getBusinessMinutesBetweenTwoTime(const.BASE_DATETIME - const.ONE_HOUR, const.BASE_DATETIME, businessHours)
    lowDowntime, _ = optimisticDowntime(const.BASE_DATETIME - const.ONE_HOUR, const.BASE_DATETIME, pollData, businessHours)
    lowUpTime = pessimisticUptime(const.BASE_DATETIME - const.ONE_HOUR, const.BASE_DATETIME, pollData, businessHours)
    _, fraction = optimisticDowntime(const.BASE_DATETIME - const.THREE_HOURS, const.BASE_DATETIME, pollData, businessHours)

    highUptime = totalBusinessMinutes - lowDowntime

    uptime = highUptime * fraction + (1-fraction) * lowUpTime
    downTime = totalBusinessMinutes - uptime
    return uptime, downTime



def generate_report(report_id):
    query.clusterStoreStatus()
    storeWithBusinessHours = query.getStoreIdWithBusinessHours()
    
    with open(f'{const.ROOTPATH}/{report_id}.csv', mode='w', newline='') as report_file:
        report_writer = csv.writer(report_file, delimiter=',')

        # Write the column names to the CSV file
        report_writer.writerow(['store_id', 'uptime_last_hour', 'uptime_last_day', 'uptime_last_week', 'downtime_last_hour', 'downtime_last_day', 'downtime_last_week'])

        for storeId, businessHours in storeWithBusinessHours:
            pollData = query.getPollData(const.BASE_DATETIME - const.ONE_WEEK, const.BASE_DATETIME, storeId)

            uptime_last_week, downtime_last_week = lastWeekUptimeAndDowntime(pollData, businessHours)
            uptime_last_day, downtime_last_day = lastDayUptimeAndDowntime(pollData, businessHours)
            uptime_last_hour, downtime_last_hour = lastHourUptime(pollData, businessHours)

            # Write the data for the current store to the CSV file
            report_writer.writerow([storeId, uptime_last_hour, uptime_last_day, uptime_last_week, downtime_last_hour, downtime_last_day, downtime_last_week])
    query.updateReport("done", report_id)
    # print current time
    print("here", datetime.datetime.now())
