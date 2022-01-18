# ######################################################################
# SESSION MANAGEMENT
# ######################################################################

SESSION_LOGIN = "public/auth"
SESSION_LOGOUT = "private/logout"
SESSION_GET_TIME = "public/get_time"
SESSION_TEST = "public/test"
SESSION_SET_HEARTBEAT = "public/set_heartbeat"
SESSION_DISABLE_HEARTBEAT = "public/disable_heartbeat"
SESSION_ENABLE_CANCEL_ON_DISCONNECT = "private/enable_cancel_on_disconnect"
SESSION_DISABLE_CANCEL_ON_DISCONNECT = "private/disable_cancel_on_disconnect"

# ######################################################################
# ACCOUNT SUMMARY
# ######################################################################

ACCOUNT_GET_POSITION = "private/get_position"
ACCOUNT_GET_POSITIONS = "private/get_positions"
ACCOUNT_GET_SUMMARY = "private/get_account_summary"

ACCOUNT_GET_ANNOUNCEMENTS = "public/get_announcements"

ACCOUNT_CREATE_SUB_ACCOUNT = "private/create_subaccount"
ACCOUNT_GET_SUB_ACCOUNTS = "private/get_subaccounts"
ACCOUNT_SET_SUB_ACCOUNT_EMAIL = "private/set_email_for_subaccount"
ACCOUNT_SET_SUB_ACCOUNT_NAME = "/private/change_subaccount_name"
ACCOUNT_SET_SUB_ACCOUNT_PASSWORD = "private/set_password_for_subaccount"
ACCOUNT_TOGGLE_SUB_ACCOUNT_LOGIN = "/private/toggle_subaccount_login"

ACCOUNT_CREATE_API_KEY = "private/create_api_key"
ACCOUNT_LIST_API_KEYS = "private/list_api_keys"
ACCOUNT_RESET_API_KEY = "private/reset_api_key"
ACCOUNT_REMOVE_API_KEY = "private/remove_api_key"
ACCOUNT_SET_API_KEY_AS_DEFAULT = "private/set_api_key_as_default"



# ######################################################################
# MARKET DATA
# ######################################################################

DATA_GET_INSTRUMENTS = "public/get_instruments"
DATA_GET_ORDER_BOOK = "public/get_order_book"
DATA_CURRENCIES = "public/get_currencies"
DATA_INDEX = "public/get_index"
DATA_LAST_TRADES_BY_INSTRUMENT = "public/get_last_trades_by_instrument"
DATA_BOOK_SUMMARY_BY_CURRENCY = "public/get_book_summary_by_currency"
DATA_BOOK_SUMMARY_BY_INSTRUMENT = "public/get_book_summary_by_instrument"

# ######################################################################
# SUBSCRIPTIONS
# ######################################################################

METHOD_SUBSCRIBE = "public/subscribe"
METHOD_UNSUBSCRIBE = "public/unsubscribe"

METHOD_PRIVATE_SUBSCRIBE = "private/subscribe"
METHOD_PRIVATE_UNSUBSCRIBE = "private/unsubscribe"


# ######################################################################
# TRADING
# ######################################################################

TRADING_BUY = "private/buy"
TRADING_SELL = "private/sell"
TRADING_CLOSE = "private/close_position"

# Order cancellation
TRADING_CANCEL_ALL = "private/cancel_all"
TRADING_CANCEL_ALL_BY_CURRENCY = "private/cancel_all_by_currency"
TRADING_CANCEL_ALL_BY_INSTRUMENT = "private/cancel_all_by_instrument"

# Margins
TRADING_COMPUTE_MARGIN = "private/get_margins"

# Open orders status
TRADING_ORDER_STATUS = "private/get_order_state"
TRADING_OPEN_ORDERS_BY_CURRENCY = "private/get_open_orders_by_currency"
TRADING_OPEN_ORDERS_BY_INSTRUMENT = "private/get_open_orders_by_instrument"

# Trade history (user)
TRADING_USER_TRADES_BY_CURRENCY = "private/get_user_trades_by_currency"
TRADING_USER_TRADES_BY_INSTRUMENT = "private/get_user_trades_by_instrument"

# ######################################################################
# TRADING
# ######################################################################

WALLET_CANCEL_TRANSFER_BY_ID = "private/cancel_transfer_by_id"
WALLET_CANCEL_WITHDRAWAL = "private/cancel_withdrawal"
WALLET_CREATE_DEPOSIT_ADDRESS = "private/create_deposit_address"
WALLET_GET_CURRENT_DEPOSIT_ADDRESS = "private/get_current_deposit_address"
WALLET_GET_DEPOSITS = "private/get_deposits"
WALLET_GET_TRANSFERS = "private/get_transfers"
WALLET_GET_WITHDRAWALS = "private/get_withdrawals"
WALLET_SUBMIT_TRANSFER_TO_SUBACCOUNT = "private/submit_transfer_to_subaccount"
WALLET_SUBMIT_TRANSFER_TO_USER = "private/submit_transfer_to_user"
WALLET_WITHDRAW = "private/withdraw"



























