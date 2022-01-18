import datetime as dt

DATE_FORMAT = "%d%b%y"
EXPIRY_HOUR_UTC_AS_TIME_DELTA = dt.timedelta(hours=8.0)


def timestamp_from_instrument_name(instrument_name):
    date_str = string_from_instrument_name(instrument_name)
    dt_obj = dt.datetime.strptime(date_str, DATE_FORMAT) + EXPIRY_HOUR_UTC_AS_TIME_DELTA
    return dt_obj.timestamp()


def string_from_instrument_name(instrument_name):
    return instrument_name.split("-")[1]


def timestamp_to_string(ts: float):
    dt_obj = dt.datetime.utcfromtimestamp(ts)
    date_str = dt_obj.strftime(DATE_FORMAT).upper()
    if date_str[0] == "0":
        return date_str[1:]
    return date_str
