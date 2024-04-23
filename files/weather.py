import datetime, random, time, string


def _get_next_weather(station_name="A"):
    # temp pattern
    month_avg = [27,31,44,58,70,79,83,81,74,61,46,32]
    shift = (random.random()-0.5) * 30
    month_avg = [m + shift + (random.random()-0.5) * 5 for m in month_avg]
    
    # rain pattern
    start_rain = [0.1,0.1,0.3,0.5,0.4,0.2,0.2,0.1,0.2,0.2,0.2,0.1]
    shift = (random.random()-0.5) * 0.1
    start_rain = [r + shift + (random.random() - 0.5) * 0.2 for r in start_rain]
    stop_rain = 0.2 + random.random() * 0.2

    # day's state
    today = datetime.date(2000, 1, 1)
    temp = month_avg[0]
    raining = False
    
    # gen weather
    while True:
        # choose temp+rain
        month = today.month - 1
        temp = temp * 0.8 + month_avg[month] * 0.2 + (random.random()-0.5) * 20
        if temp < 32:
            raining=False
        elif raining and random.random() < stop_rain:
            raining = False
        elif not raining and random.random() < start_rain[month]:
            raining = True

        yield (today.strftime("%Y-%m-%d"), station_name, temp, raining)

        # next day
        today += datetime.timedelta(days=1)


def get_next_weather(count=10, sleep_sec=0.1):
    assert count <= 26
    stations = []
    for station_name in string.ascii_uppercase[:count]:
        stations.append(_get_next_weather(station_name))
    while True:
        for station in stations:
            yield next(station)
        time.sleep(sleep_sec)


# Example usage
# for date, station_name, temp, raining in get_next_weather():
#     print(date, station_name, temp, raining)