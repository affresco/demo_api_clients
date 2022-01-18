import datetime as dt
from typing import Dict

import numpy as np
from scipy.interpolate import interp1d

from containers.quote import SimpleQuote


# ####################################################################
# VOLATILITY SMILE
# ####################################################################

class VolatilitySmile(object):
    """
    Container class for a volatility smile including bid and ask sub-smiles.
    """

    def __init__(self, expiry: float, bid: Dict, ask: Dict, forward: SimpleQuote):

        # Required
        self.expiry = self.__sanitize_expiry(expiry)

        # Bid/Ask of implied volatility level
        self.bid = OneSidedVolatilitySmile(forward=forward.bid, data=bid)
        self.ask = OneSidedVolatilitySmile(forward=forward.ask, data=ask)

        # self.forward = SimpleQuote.instance(forward)
        self.forward = forward

    @classmethod
    def __sanitize_expiry(cls, expiry):
        if isinstance(expiry, dt.datetime):
            return expiry.timestamp()
        if isinstance(expiry, float):
            return expiry
        raise TypeError()

    @classmethod
    def instance(cls, bid, ask, expiry):
        expiry = dt.datetime.strptime(expiry, "%d%b%y").timestamp()
        forward_bid, forward_ask = bid["forward"], ask["forward"]
        forward = SimpleQuote(bid=forward_bid, ask=forward_bid, expiry=expiry)
        bid, ask = bid["smile"], ask["smile"]
        return VolatilitySmile(expiry=expiry, bid=bid, ask=ask, forward=forward)


# ####################################################################
# VOLATILITY SMILE ON ONE SIDE (BID OR ASK)
# ####################################################################

class OneSidedVolatilitySmile(object):
    """
    Container class for a volatility smile including only one sub-smile,
    either bid or ask.
    """
    def __init__(self, data: Dict, forward: SimpleQuote = None):
        self.forward = forward
        self.data = self.__sanitize_data(data)
        self.model = self.__set_model()

    @classmethod
    def __sanitize_data(cls, data: Dict):
        return {float(k): float(v) for k, v in data.items()}

    def __set_model(self):
        kind = "cubic" if len(self.data) > 10 else "linear"
        xs = list(self.data.keys())
        ys = list(self.data.values())
        return interp1d(xs, ys, kind=kind, fill_value="extrapolate")

    def as_numpy_array(self):
        a = np.array([list(self.data.keys()),
                      list(self.data.values())])
        return a.transpose()

    def __call__(self, strike, *args, **kwargs):

        if isinstance(strike, float):

            if strike <= min(self.data.keys()):
                return self.data[min(self.data.keys())]

            if strike >= max(self.data.keys()):
                return self.data[max(self.data.keys())]

            res = self.model(strike)
            return float(res)

        else:
            return self.model(strike)
