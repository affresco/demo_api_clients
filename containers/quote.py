from typing import Dict


# ####################################################################
# QUOTE
# ####################################################################

class SimpleQuote(object):
    """
    Container for bid/ask quote provided as two floats.
    Can also be provided with an expiry and a strike for contextual purposes.
    """

    def __init__(self, bid: float = None, ask: float = None,
                 expiry: float = None, strike: float = None,
                 **kwargs):
        self.bid = bid
        self.ask = ask
        self.mid = None
        self.expiry = expiry
        self.strike = strike
        self.sanitize(**kwargs)

    @classmethod
    def instance(cls, data):
        if isinstance(data, SimpleQuote):
            return data
        if isinstance(data, Dict):
            return SimpleQuote(**data)
        raise TypeError()

    def sanitize(self, **kwargs):

        if "mid" in kwargs:

            # Assign
            self.mid = kwargs["mid"]

            # Redirect the bid/ask requests
            if self.bid is None and self.ask is None:
                self.bid = self.mid
                self.ask = self.mid
        else:
            self. mid = 0.5 * (self.bid + self.ask)

    def to_dict(self):
        return {"bid": self.bid, "ask": self.ask}