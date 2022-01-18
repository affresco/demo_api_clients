from blinker import Signal

quotes = Signal("DELTA-QUOTE-NOTIFICATION")
trades = Signal("DELTA-TRADE-NOTIFICATION")
orderbooks = Signal("DELTA-ORDERBOOK-NOTIFICATION")
indices = Signal("DELTA-INDEX-NOTIFICATION")
announcements = Signal("DELTA-ANNOUNCEMENT-NOTIFICATION")

