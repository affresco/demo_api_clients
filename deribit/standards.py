INSTRUMENT_SYMBOL_KEY = "instrument_name"
CURRENCY_SYMBOL_KEY = "currency"

DEFAULT_KINDS = ["future", "option"]
DEFAULT_CURRENCIES = ["BTC", "ETH"]

HTTP_REQUEST_PAYLOAD_KEY = "result"

DELTA_TIMESTAMP_SCALING = 0.001

PERPETUAL_SUFFIX = "PERPETUAL"
PERPETUAL_SWAPS = ['-'.join([ccy, PERPETUAL_SUFFIX]) for ccy in DEFAULT_CURRENCIES]