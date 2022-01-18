from ..support.sanitizers import sanitize
from .common import message, add_params_to_message
from ..support.endpoints import *

from utilities.marshal import to_list

from deribit.standards import DEFAULT_CURRENCIES, DEFAULT_KINDS

API_KEY_NAME_MAX_CHARS = 16


# ######################################################################
# POSITIONS
# ######################################################################

def get_position(instrument: str):
    """
    Create a message to get all positions for a contract/instrument on delta.
    :param instrument: Contract (str) on delta (e.g. 'BTC-PERPETUAL' or 'BTC-1NOV-8000-C')
    :return: Message (dict)
    """
    data = sanitize(instrument=instrument)
    msg = message(method=ACCOUNT_GET_POSITION)
    return add_params_to_message({"instrument_name": data["instrument"]}, msg)


def get_all_positions(currency=None, kind=None):
    """
    Create a message to get all positions for a given currency on delta.
    :param currency: String symbol (e.g. 'BTC' or 'ETH')
    :param kind: Type of contract (either 'future' or 'option')
    :return: Message (dict)
    """

    # Defaults
    currency = currency or DEFAULT_CURRENCIES
    kind = kind or DEFAULT_KINDS

    # Marshal
    currency = to_list(currency)
    kind = to_list(kind)

    # Loop to produce messages
    output = []
    for k in kind:
        for ccy in currency:
            output.append(__get_all_positions_for_ccy_and_kind(ccy, k))
    return output


def __get_all_positions_for_ccy_and_kind(currency: str, kind: str):
    """
    Create a message to get all positions for a given currency on delta.
    :param currency: String symbol (e.g. 'BTC' or 'ETH')
    :param kind: Type of contract (either 'future' or 'option')
    :return: Message (dict)
    """
    data = sanitize(currency=currency, kind=kind)
    msg = message(method=ACCOUNT_GET_POSITIONS)
    params = {"currency": data["currency"].upper(), "kind": data["kind"].lower()}
    return add_params_to_message(params, msg)


# ######################################################################
# SUMMARY
# ######################################################################


def get_account_summary(currency: str, extended=True):
    """
    Create a message to get a summary of the delta account.
    :param currency: String symbol (e.g. BTC or ETH)
    :param extended: Bool to get a long version of the resulting summary.
    :return: Message (dict)
    """
    data = sanitize(currency=currency)
    msg = message(method=ACCOUNT_GET_SUMMARY)
    params = {"currency": data["currency"].upper(), "extended": extended}
    return add_params_to_message(params, msg)


# ######################################################################
# ANNOUNCEMENTS
# ######################################################################

def get_announcements():
    """
    Create a message to retrieve the announcements from deribit.
    :return: Message (dict)
    """
    msg = message(method=ACCOUNT_GET_ANNOUNCEMENTS)
    return add_params_to_message({}, msg)


# ######################################################################
# SUB-ACCOUNTS
# ######################################################################

def get_create_sub_account():
    """
    Create a message to create a sub-account on delta.
    :return: Message (dict)
    """
    msg = message(method=ACCOUNT_CREATE_SUB_ACCOUNT)
    return add_params_to_message({}, msg)


def get_sub_accounts(with_portfolio: bool = False):
    """
    Create a message to get a list of all sub-accounts.
    :param with_portfolio: Bool to include portfolio summary in response
    :return: Message (dict)
    """
    msg = message(method=ACCOUNT_GET_SUB_ACCOUNTS)
    params = {"with_portfolio": with_portfolio}
    return add_params_to_message(params, msg)


def change_name_of_sub_account(id_, name):
    """
    Create a message to set the email for a given sub-account.
    :param id_: Integer representing the account ID number
    :param name: Name as string
    :return: Message (dict)
    """
    msg = message(method=ACCOUNT_SET_SUB_ACCOUNT_NAME)
    params = {"sid": str(id_), "name": str(name)}
    return add_params_to_message(params, msg)


# TODO: NOT TESTED... COMPLETE
def set_email_for_sub_account(account_id, email):
    """
    Create a message to set the email for a given sub-account.
    :param account_id: Integer representing the account ID number
    :param email: Email address as string
    :return: Message (dict)
    """
    data = sanitize(account_id=account_id, email=email)
    msg = message(method=ACCOUNT_SET_SUB_ACCOUNT_EMAIL)
    params = {"sid": data["account_id"], "email": data["email"]}
    return add_params_to_message(params, msg)


# TODO: NOT TESTED... COMPLETE
def set_password_for_sub_account(account_id, password):
    """
    Create a message to set the password for a given sub-account.
    :param account_id: Integer representing the ID of the account
    :param password: String representing the password for the sub-account
    :return: Message (dict)
    """
    data = sanitize(account_id=account_id, password=password)
    msg = message(method=ACCOUNT_GET_SUB_ACCOUNTS)
    params = {"sid": data["account_id"], "password": data["password"]}
    return add_params_to_message(params, msg)


# ######################################################################
# API KEYS
# ######################################################################

# TODO: NOT TESTED... COMPLETE
def list_api_keys():
    """
    Create a message to get a list of all API keys.
    :return: Message (dict)
    """
    msg = message(method=ACCOUNT_GET_SUB_ACCOUNTS)
    return add_params_to_message({}, msg)


# TODO: NOT TESTED... COMPLETE
def reset_api_key(key_id: int):
    """
    Create a message to reset an API key.
    :param key_id: Integer representing the ID of the API key
    :return: Message (dict)
    """
    data = sanitize(key_id=key_id)
    msg = message(method=ACCOUNT_RESET_API_KEY)
    params = {"id": data["key_id"]}
    return add_params_to_message(params, msg)


# TODO: NOT TESTED... COMPLETE
def remove_api_key(key_id: int):
    """
    Create a message to delete an API key.
    :param key_id: Integer representing the ID of the API key
    :return: Message (dict)
    """
    data = sanitize(key_id=key_id)
    msg = message(method=ACCOUNT_REMOVE_API_KEY)
    params = {"id": data["key_id"]}
    return add_params_to_message(params, msg)


# TODO: NOT TESTED... COMPLETE
def set_api_key_as_default(key_id: int):
    """
    Create a message to set an API key as default.
    :param key_id:  Integer representing the ID of the API key
    :return: Message (dict)
    """
    data = sanitize(key_id=key_id)
    msg = message(method=ACCOUNT_SET_API_KEY_AS_DEFAULT)
    params = {"id": data["key_id"]}
    return add_params_to_message(params, msg)


# TODO: NOT TESTED... COMPLETE
def create_api_key(account: str = None, trade: str = None,
                   block_trade: str = None, wallet: str = None,
                   default: bool = False, name: str = None):
    """
    Create a message to set an API key as default.
    :param account:  Access to account info (read, read_write, none)
    :param trade:  Access to trading (read, read_write, none)
    :param block_trade:  Allowed to do block trades (read, read_write, none)
    :param wallet:  Access to wallet (read, read_write, none)
    :param default:  Is this the default key for the account
    :param name:  Short name (user readable, max 16 chars)
    :return: Message (dict)
    """

    # Default scopes ('none')
    account = str(account).lower() or "read"
    trade = str(trade).lower() or "read"
    wallet = str(wallet).lower() or "none"
    block_trade = str(block_trade).lower() or "none"
    scope = " ".join([f"account:{account}",
                      f"trade:{trade}",
                      f"block_trade:{block_trade}",
                      f"wallet:{wallet}"])

    params = {"max_scope": scope}
    if name:
        params["name"] = str(name)[0:API_KEY_NAME_MAX_CHARS]
    if default:
        params["default"] = bool(default)

    msg = message(method=ACCOUNT_CREATE_API_KEY)
    return add_params_to_message(params, msg)
