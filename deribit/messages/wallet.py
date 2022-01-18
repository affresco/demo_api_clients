from ..support.sanitizers import sanitize
from ..messages.common import message, add_params_to_message
from ..support.endpoints import *


# ######################################################################
# TRANSFER
# ######################################################################

# TODO: NOT TESTED... COMPLETE
def cancel_transfer_by_id(currency, transfer_id, tfa=None):
    """
    Create a message to cancel a transfer using its ID number.
    :param currency: String symbol (e.g. BTC or ETH)
    :param transfer_id: Integer ID for the transfer
    :param tfa: Two-factor authentication
    :return: Message (dict)
    """
    data = sanitize(currency=currency, transfer_id=transfer_id, tfa=tfa)
    msg = message(method=WALLET_CANCEL_TRANSFER_BY_ID)
    params = {"currency": data["currency"], "transfer_id": data["transfer_id"]}
    if tfa:
        params["tfa"] = data["tfa"]
    return add_params_to_message(params, msg)


# TODO: NOT TESTED... COMPLETE
def get_transfers(currency, count, offset):
    """
    Create a message to request all transfers for a given currency.
    :param currency: String symbol (e.g. BTC or ETH)
    :param count: Integer for the max number of transfers requested.
    :param offset: N/A  # TODO CONFIRM WHAT THIS IS
    :return: Message (dict)
    """
    data = sanitize(currency=currency, count=count, offset=offset)
    msg = message(method=WALLET_GET_TRANSFERS)
    params = {"currency": data["currency"], "count": data["count"], "offset": data["offset"]}
    return add_params_to_message(params, msg)


# TODO: NOT TESTED... COMPLETE
def submit_transfer_to_subaccount(currency, amount, destination):
    """
    Create a message to make a transfer to a sub-account.
    :param currency: String symbol (e.g. BTC or ETH)
    :param amount: Float in cryptocurrency.
    :param destination: Sub-account identified by... # TODO NO IDEA HOW THIS GETS REPRESENTED...
    :return: Message (dict)
    """
    data = sanitize(currency=currency, amount=amount, destination=destination)
    msg = message(method=WALLET_SUBMIT_TRANSFER_TO_SUBACCOUNT)
    params = {"currency": data["currency"], "amount": data["amount"], "destination": data["destination"]}
    return add_params_to_message(params, msg)


# TODO: NOT TESTED... COMPLETE
def submit_transfer_to_user(currency, amount, destination, tfa=None):
    """
    Create a message to
    :param currency: String symbol (e.g. BTC or ETH)
    :param amount: Float in cryptocurrency.
    :param destination: User identified by... # TODO NO IDEA HOW THIS GETS REPRESENTED...
    :param tfa: Two-factor authentication
    :return: Message (dict)
    """
    data = sanitize(currency=currency, amount=amount, destination=destination, tfa=tfa)
    msg = message(method=WALLET_SUBMIT_TRANSFER_TO_USER)
    params = {"currency": data["currency"], "amount": data["amount"], "destination": data["destination"]}
    if tfa:
        params["tfa"] = data["tfa"]
    return add_params_to_message(params, msg)


# ######################################################################
# WITHDRAWAL
# ######################################################################

# TODO: NOT TESTED... COMPLETED
def cancel_withdrawal(currency, id):
    """
    Create a message to cancel a withdrawal from delta by its ID.
    :param currency: String symbol (e.g. BTC or ETH)
    :param id: Integer representing the ID of the operation
    :return: Message (dict)
    """
    data = sanitize(currency=currency, id=id)
    msg = message(method=WALLET_CANCEL_WITHDRAWAL)
    params = {"currency": data["currency"], "id": data["id"]}
    return add_params_to_message(params, msg)


# TODO: NOT TESTED... COMPLETED
def get_withdrawals(currency, count, offset):
    """
    Create a message to get a list of withdrawals from delta API.
    :param currency: String symbol (e.g. BTC or ETH)
    :param count: Integer for the max number of withdrawals requested.
    :param offset: N/A
    :return: Message (dict)
    """
    data = sanitize(currency=currency, count=count, offset=offset)
    msg = message(method=WALLET_GET_WITHDRAWALS)
    params = {"currency": data["currency"], "count": data["count"], "offset": data["offset"]}
    return add_params_to_message(params, msg)


# TODO: NOT TESTED... COMPLETED
def withdraw(currency, address, amount, priority, tfa=None):
    """
    Create a message to request a withdrawal from deribit.
    :param currency: String symbol (e.g. BTC or ETH)
    :param address: Address to which the cryptocurrency will be sent.
    :param amount: Float in cryptocurrency.
    :param priority: String representing the priority (e.g. 'low' or 'high') # TODO CONFIRM THIS
    :param tfa: Two-factor authentication
    :return: Message (dict)
    """
    data = sanitize(currency=currency, address=address, amount=amount, priority=priority, tfa=tfa)
    msg = message(method=WALLET_SUBMIT_TRANSFER_TO_USER)
    params = {"currency": data["currency"],
              "address": data["address"],
              "amount": data["amount"],
              "priority": data["priority"]}
    if tfa:
        params["tfa"] = data["tfa"]
    return add_params_to_message(params, msg)


# ######################################################################
# DEPOSIT
# ######################################################################

# TODO: NOT TESTED... COMPLETED
def create_deposit_address(currency):
    """
    Create a message to create a new deposit address on delta.
    :param currency: String symbol (e.g. BTC or ETH)
    :return: Message (dict)
    """
    data = sanitize(currency=currency)
    msg = message(method=WALLET_CREATE_DEPOSIT_ADDRESS)
    params = {"currency": data["currency"]}
    return add_params_to_message(params, msg)


# TODO: NOT TESTED... COMPLETED
def get_current_deposit_address(currency):
    """
    Create a message to queries the current deposit address from delta API.
    :param currency: String symbol (e.g. BTC or ETH)
    :return: Message (dict)
    """
    data = sanitize(currency=currency)
    msg = message(method=WALLET_GET_CURRENT_DEPOSIT_ADDRESS)
    params = {"currency": data["currency"]}
    return add_params_to_message(params, msg)


# TODO: NOT TESTED... COMPLETED
def get_deposits(currency, count, offset):
    """
    Create a message to get a list of deposits from delta API.
    :param currency: String symbol (e.g. BTC or ETH)
    :param count: Integer for the max number of deposits requested.
    :param offset: N/A # TODO CONFIRM WHAT THIS IS
    :return: Message (dict)
    """
    data = sanitize(currency=currency, count=count, offset=offset)
    msg = message(method=WALLET_GET_DEPOSITS)
    params = {"currency": data["currency"],
              "count": data["count"],
              "amount": data["amount"],
              "offset": data["offset"]}
    return add_params_to_message(params, msg)






























# the end
