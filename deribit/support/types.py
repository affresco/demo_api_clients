from enum import Enum


# ######################################################################
# CONSTANTS
# ######################################################################

class INSTRUMENT_KIND(Enum):
    FUTURE = "future"
    OPTION = "option"
    ANY = "any"


class INSTRUMENT_CURRENCY(Enum):
    BITCOIN = "btc"
    ETHER = "eth"


class ORDER_BOOK_GROUP(Enum):
    ONE = 1
    TWO = 2
    FIVE = 5
    TEN = 10
    TWENTY_FIVE = 25
    ONE_HUNDRED = 100
    TWO_HUNDRED_FIFTY = 250


class INTERVAL(Enum):
    STANDARD = "100ms"
    RAW = "raw"


class PUBLIC_CHANNELS(Enum):
    ORDERBOOK_UPDATES = "book"
    QUOTES = "quote"
    TRADES = "trades"
    ANNOUNCEMENTS = "announcements"


class ORDER_TYPE(Enum):
    LIMIT = "limit"
    MARKET = "market"
    STOP_LIMIT = "stop-limit"
    STOP_MARKET = "stop-market"
    ALL = "all"


class TIME_IN_FORCE(Enum):
    GOOD_TIL_CANCELLED = "good_til_cancelled"
    FILL_OR_KILL = "fill_or_kill"
    IMMEDIATE_OR_CANCEL = "immediate_or_cancel"


class TRIGGER_PRICE(Enum):
    INDEX = "index_price"
    MARK = "mark_price"
    LAST = "last_price"


class ADVANCED_QUOTE_TYPE(Enum):
    USD = "usd"
    IMP_VOL = "implv"
