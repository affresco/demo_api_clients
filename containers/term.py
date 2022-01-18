import datetime as dt
from typing import Dict
from scipy.interpolate import interp1d

from containers.quote import SimpleQuote

from utilities.time import timestamp_to_year_fraction as ts2ttm

# ####################################################################
# CONSTANTS
# ####################################################################

# If the key of the term structure,
# supposed to be in year fraction,
# is greater than 1000 years then we assume
# that the data is in fact in timestamp (seconds)
# and it must be transformed
DATETIME_TTM_THRESHOLD = 1000.0

__all__ = ["TermStructure"]


# ####################################################################
# TERM STRUCTURE (E.G. FORWARD)
# ####################################################################

class TermStructure(object):
    """
    Container for bid/ask term structures provided as two dict of
    key-value pairs {ttm (year fraction): level}
    """

    def __init__(self, spot, bid, ask):
        self.spot = SimpleQuote.instance(spot)
        self.bid = self.OneSidedTermStructure(spot=self.spot.bid, data=bid)
        self.ask = self.OneSidedTermStructure(spot=self.spot.ask, data=ask)

    def __call__(self, ttm, direction):

        if "bid" in direction:
            return self.bid(ttm=ttm)

        if "ask" in direction:
            return self.ask(ttm=ttm)

        raise Exception()

    class OneSidedTermStructure(object):
        """
        Container for single sided term structures,
        either bid or ask, provided as two dict of
        key-value pairs {ttm (year fraction): level}
        """

        def __init__(self, spot: float, data: Dict):
            self.spot = float(spot)
            self.data = self.__sanitize(data)
            self.model = self.__set_model()

        @classmethod
        def __sanitize(cls, data: Dict):

            data = {float(k): float(v) for k, v in data.items()}
            max_ttm = max(data.keys())

            if max_ttm < DATETIME_TTM_THRESHOLD:
                return data

            f = dt.datetime.utcnow().timestamp()
            return {ts2ttm(f, ttm): float(fwd) for ttm, fwd in data.items()}

        def __set_model(self):
            kind = "cubic" if len(self.data) > 10 else "linear"
            xs = list(self.data.keys())
            ys = list(self.data.values())
            return interp1d(xs, ys, kind=kind)

        def __call__(self, ttm, *args, **kwargs):

            if ttm < 0.0:
                ttm = 0.0

            if ttm > DATETIME_TTM_THRESHOLD:
                ttm = ts2ttm(dt.datetime.utcnow().timestamp(), ttm)

            if ttm >= max(self.data.keys()):
                return self.data[max(self.data.keys())]

            res = self.model(ttm)
            return float(res)
