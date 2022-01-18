"""

from blinker import signal

# ##################################################################
# LOGIN / LOGOUT
# ##################################################################

login = signal("delta-LOGIN")
logout = signal("delta-LOGOUT")

# ##################################################################
# MARKET DATA
# ##################################################################

instrument_received = signal("delta-INSTRUMENTS-RECEIVED")
index_level_received = signal("delta-INDEX-LEVEL-RECEIVED")
currency_received = signal("delta-CURRENCY-RECEIVED")
orderbook_snapshot_received = signal("delta-ORDERBOOK-SNAPSHOT-RECEIVED")


# ##################################################################
# ACCOUNT
# ##################################################################

position_received = signal("delta-ACCOUNT-POSITION-RECEIVED")
all_positions_received = signal("delta-ACCOUNT-POSITIONS-RECEIVED")
account_summary = signal("delta-ACCOUNT-SUMMARY-RECEIVED")
announcement = signal("delta-ACCOUNT-ANNOUNCEMENT-RECEIVED")

# ##################################################################
# TRADING
# ##################################################################

trade_buy_received = signal("delta-TRADE-BUY-RECEIVED")
trade_sell_received = signal("delta-TRADE-SELL-RECEIVED")
trade_close_received = signal("delta-TRADE-CLOSE-RECEIVED")
trade_cancel_received = signal("delta-TRADE-CANCEL-RECEIVED")
trade_cancel_all_received = signal("delta-TRADE-CANCEL-ALL-RECEIVED")
trade_margin_estimate_received = signal("delta-TRADE-MARGIN-ESTIMATE-RECEIVED")
trade_open_orders_received = signal("delta-TRADE-OPEN-ORDERS-RECEIVED")
trade_history_received = signal("delta-TRADE-HISTORY-RECEIVED")
trade_order_status_received = signal("delta-TRADE-ORDER-STATUS-RECEIVED")
"""