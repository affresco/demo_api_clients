import datetime as dt

# ####################################################################
# LINEAR
# ####################################################################

SECONDS_PER_DAY = 86400  # 24 * 60 * 60
TRD_DAYS_PER_YEAR = 365.2421875  # source: NASA


# ####################################################################
# LINEAR
# ####################################################################

def month_to_int(month: str):
    calendar = {"JAN": 1, "FEB": 2, "MAR": 3,
                "APR": 4, "MAY": 5, "JUN": 6,
                "JUL": 7, "AUG": 8, "SEP": 9,
                "OCT": 10, "NOV": 11, "DEC": 12}
    return calendar[month.upper()]


def int_to_month(month: int):
    calendar = {1: "JAN", 2: "FEB", 3: "MAR",
                4: "APR", 5: "MAY", 6: "JUN",
                7: "JUL", 8: "AUG", 9: "SEP",
                10: "OCT", 11: "NOV", 12: "DEC"}
    return calendar[month]


# ####################################################################
# LINEAR
# ####################################################################

def time_to_expiry(expiry: float = None,
                   filtration: float = None,
                   days_per_year: float = TRD_DAYS_PER_YEAR,
                   ttm: float = None,
                   **kwargs):
    """
    Compute the time to expiry (TTM) as a year fraction.
    :param expiry: Timestamp (float)
    :param filtration: Timestamp (float)
    :param days_per_year: Number of trading days per year (default 365.25)
    :param ttm: Allow for a pre-computed TTM to be passed-in, which is returned immediately
    :param kwargs: n/a
    :return: Time to maturity as a year fraction (float, e.g. 1.21545)
    """

    # compute_ttm value already computed, returned directly
    if ttm is not None:
        return ttm

    # spot (perpetual) must return a compute_ttm of 0
    max_timestamp = dt.datetime(2099, 12, 31).timestamp()
    if expiry > max_timestamp:
        return 0.0

    # Presume valid expiry date
    elif expiry is not None:

        seconds_per_year = SECONDS_PER_DAY * days_per_year

        if filtration is not None:
            return float((expiry - filtration) / seconds_per_year)
        else:
            return float((expiry - dt.datetime.utcnow().timestamp()) / seconds_per_year)

    # Impossible to compute compute_ttm
    else:
        raise ValueError(f"Inconsistent filtration ({filtration}) and expiry ({expiry}) dates received.")


def timestamp_to_datetime(timestamp: float):
    return dt.datetime.fromtimestamp(timestamp)


def datetime_to_timestamp(datetime: dt.datetime):
    return datetime.timestamp()


def timestamp_to_year_fraction(start_date, end_date, days_per_year=TRD_DAYS_PER_YEAR):
    return (end_date - start_date) / (days_per_year * SECONDS_PER_DAY)


def timedelta_to_year_fraction(time_delta: dt.timedelta, days_per_year=TRD_DAYS_PER_YEAR):
    return seconds_to_year_fraction(time_delta.total_seconds(), days_per_year)


def seconds_to_year_fraction(seconds, days_per_year=TRD_DAYS_PER_YEAR):
    yr_ = dt.timedelta(days=days_per_year)
    return seconds / yr_.total_seconds()
