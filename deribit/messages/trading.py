from typing import Dict

from ..support.sanitizers import sanitize
from ..messages.common import message, add_params_to_message
from ..support.types import ORDER_TYPE
from ..support.endpoints import *


# ######################################################################
# REQUESTS
# ######################################################################

def buy(instrument: str, amount: float, order_type: str = None, label: str = None,
        limit_price: float = None, time_in_force: str = None, max_show: float = None, post_only: bool = False,
        reduce_only: bool = False, stop_price: float = None, trigger: str = None, vol_quote: bool = False):
    """
    Generates a 'buy' message for delta API.
    :param instrument: (str) delta instrument's name
    :param amount: (float) Amount in USD for future or BTC (or ETH) for options
    :param order_type: (str) Order type. Either containers, limit, stop_limit, stop_market.
    :param label: My own label / id for this message.
    :param limit_price: Limit price, required for LIMIT and STOP_LIMIT orders.
    :param time_in_force: (str) Time in force. Either GTC, FOK, IOC.
    :param max_show: Maximum amount to be shown to other customers. 0 is invisible order.
    :param post_only: (bool) If the new price would cause the order to be filled immediately (as taker), the price will be changed to be just below the bid.
    :param reduce_only: (bool The order is intended to only reduce a current position.
    :param stop_price: (float) Stop price, required for STOP_LIMIT orders.
    :param trigger: Type of trigger to determine STOP LIMIT.
    :param vol_quote: (bool) True to enter price in vol (e.g. 1.0 for 100%). False to quote in USD.
    :return: (dict) message to be dumped to the websocket.
    """

    # Implement delta default behaviour
    if not order_type:
        order_type = ORDER_TYPE.LIMIT.value.lower()

    data = sanitize(instrument_name=instrument,
                    amount=amount,
                    type=order_type,
                    label=label,
                    limit_price=limit_price,
                    time_in_force=time_in_force,
                    max_show=max_show,
                    post_only=post_only,
                    reduce_only=reduce_only,
                    stop_price=stop_price,
                    trigger=trigger,
                    advanced=vol_quote)

    # Asset the coherence of a limit order
    limit_price_ = None if "limit_price" not in data else data["limit_price"]
    assert_limit_order_coherence(order_type=data["type"], limit_price=limit_price_)

    # Asset the coherence of a stop order
    stop_price_ = None if "stop_price" not in data else data["stop_price"]
    assert_stop_order_coherence(order_type=data["type"],
                                buy_order=True,
                                data=data,
                                stop_price=stop_price_,
                                limit_price=limit_price_)

    # Build basic message
    msg = message(method=TRADING_BUY)
    params = {key: value for (key, value) in data.items()}
    return add_params_to_message(params, msg)


def sell(instrument: str, amount: float, order_type: str = None, label: str = None,
         limit_price: float = None, time_in_force: str = None, max_show: float = None, post_only: bool = False,
         reduce_only: bool = False, stop_price: float = None, trigger: str = None, vol_quote: bool = False):
    """
    Generates a 'sell' message for delta API.
    :param instrument: (str) delta instrument's name
    :param amount: (float) Amount in USD for future or BTC (or ETH) for options
    :param order_type: (str) Order type. Either containers, limit, stop_limit, stop_market.
    :param label: My own label / id for this message.
    :param limit_price: Limit price, required for LIMIT and STOP_LIMIT orders.
    :param time_in_force: (str) Time in force. Either GTC, FOK, IOC.
    :param max_show: Maximum amount to be shown to other customers. 0 is invisible order.
    :param post_only: (bool) If the new price would cause the order to be filled immediately (as taker), the price will be changed to be just below the bid.
    :param reduce_only: (bool The order is intended to only reduce a current position.
    :param stop_price: (float) Stop price, required for STOP_LIMIT orders.
    :param trigger: Type of trigger to determine STOP LIMIT.
    :param vol_quote: (bool) True to enter price in vol (e.g. 1.0 for 100%). False to quote in USD.
    :return: (dict) message to be dumped to the websocket.
    """

    # Implement delta default behaviour
    if not order_type:
        order_type = ORDER_TYPE.LIMIT.value.lower()

    data = sanitize(instrument_name=instrument,
                    amount=amount,
                    type=order_type,
                    label=label,
                    limit_price=limit_price,
                    time_in_force=time_in_force,
                    max_show=max_show,
                    post_only=post_only,
                    reduce_only=reduce_only,
                    stop_price=stop_price,
                    trigger=trigger,
                    advanced=vol_quote)

    # Asset the coherence of a limit order
    limit_price_ = None if "limit_price" not in data else data["limit_price"]
    assert_limit_order_coherence(order_type=data["type"], limit_price=limit_price_)

    # Asset the coherence of a stop order
    stop_price_ = None if "stop_price" not in data else data["stop_price"]
    assert_stop_order_coherence(order_type=data["type"],
                                buy_order=False,
                                data=data,
                                stop_price=stop_price_,
                                limit_price=limit_price_)

    # Build basic message
    msg = message(method=TRADING_SELL)
    params = {key: value for (key, value) in data.items()}
    return add_params_to_message(params, msg)


def close(instrument: str, order_type: str = None, limit_price: float = None):
    """
    Generates a 'sell' message for delta API.
    :param instrument: (str) delta instrument's name
    :param order_type: (str) Order type. Either containers, limit, stop_limit, stop_market.
    :param limit_price: Limit price, required for LIMIT and STOP_LIMIT orders.
    :return: (dict) Message to be sent into the websocket.
    """

    data = sanitize(instrument=instrument,
                    type=order_type,
                    limit_price=limit_price)

    # Asset the coherence of a limit order
    limit_price_ = None if "limit_price" not in data else data["limit_price"]
    assert_limit_order_coherence(order_type=data["type"], limit_price=limit_price_)

    # Build basic message
    msg = message(method=TRADING_CLOSE)
    params = {key: value for (key, value) in data.items()}
    return add_params_to_message(params, msg)


def cancel_all():
    """
    Generates a 'cancellation' message for delta API : ALL instruments in ALL currencies.
    :return: (dict) Message to be sent into the websocket.
    """
    msg = message(method=TRADING_CANCEL_ALL)
    return add_params_to_message([], msg)


def cancel_all_by_currency(currency: str, kind: str = None, order_type: str = None):
    """
    Generates a 'cancellation' message for delta API for ALL instruments in a given currency.
    :param currency: (str) delta instrument's name
    :param kind: (str) Kind of instrument. Either 'future' or 'option'
    :param order_type: (str) Order type. Either containers, limit, stop_limit, stop_market.
    :return: (dict) Message to be sent into the websocket.
    """

    # Implement delta default behaviour
    if not order_type:
        order_type = ORDER_TYPE.ALL.value.lower()

    data = sanitize(currency=currency, kind=kind, type=order_type)
    assert_cancellation_order_type(order_type=data["type"])

    # Build basic message
    msg = message(method=TRADING_CANCEL_ALL_BY_CURRENCY)
    params = {key: value for (key, value) in data.items()}
    return add_params_to_message(params, msg)


def cancel_all_by_instrument(instrument: str, order_type: str = None):
    """
    Generates a 'cancellation' message for delta API for ALL instruments in a given instrument.
    :param instrument: (str) delta instrument's name
    :param order_type: (str) Order type. Either limit or stop.
    :return: (dict) Message to be sent into the websocket.
    """

    # Implement delta default behaviour
    if not order_type:
        order_type = ORDER_TYPE.ALL.value.lower()

    data = sanitize(instrument=instrument, type=order_type)
    assert_cancellation_order_type(order_type=data["type"])

    # Build basic message
    msg = message(method=TRADING_CANCEL_ALL_BY_INSTRUMENT)
    params = {key: value for (key, value) in data.items()}
    return add_params_to_message(params, msg)


def margins(instrument: str, amount: float = None, price: float = None):
    """
    Generates a request for qn estimated margins for a trade.
    :param instrument: (str) delta instrument's name
    :param amount: (float) Amount in USD for future or BTC (or ETH) for options
    :param price: (float) Estimated price for the trade.
    :return: (dict) Message to be sent into the websocket.
    """

    data = sanitize(instrument=instrument, amount=amount, price=price)

    # Build basic message
    msg = message(method=TRADING_COMPUTE_MARGIN)
    params = {key: value for (key, value) in data.items()}
    return add_params_to_message(params, msg)


def open_orders_by_currency(currency: str, kind: str = None, order_type: float = None):
    """
    Request all open orders for a given currency.
    :param currency: (str) delta instrument's name
    :param kind: (str) Kind of instrument. Either 'future' or 'option'
    :param order_type: (str) Order type. Either containers, limit, stop_limit, stop_market.
    :return: (dict) Message to be sent into the websocket.
    """

    # Implement delta default behaviour
    if not order_type:
        order_type = ORDER_TYPE.ALL.value.lower()

    data = sanitize(currency=currency, kind=kind, type=order_type)

    # Build basic message
    msg = message(method=TRADING_OPEN_ORDERS_BY_CURRENCY)
    params = {key: value for (key, value) in data.items()}
    return add_params_to_message(params, msg)


def open_orders_by_instrument(instrument: str, order_type: float = None):
    """
    Request all open orders for a given instrument.
    :param instrument: (str) delta instrument's name
    :param order_type: (str) Order type. Either containers, limit, stop_limit, stop_market.
    :return: (dict) Message to be sent into the websocket.
    """

    # Implement delta default behaviour
    if not order_type:
        order_type = ORDER_TYPE.ALL.value.lower()

    data = sanitize(instrument=instrument, type=order_type)

    # Build basic message
    msg = message(method=TRADING_OPEN_ORDERS_BY_INSTRUMENT)
    params = {key: value for (key, value) in data.items()}
    return add_params_to_message(params, msg)


def user_trades_by_currency(currency: str, kind: str = None, count: int = None,
                            include_old: bool = False):
    """
    Request all open user_trades for a given currency.
    :param currency: (str) delta instrument's name
    :param kind: (str) Kind of instrument. Either 'future' or 'option'
    :param count: (int) The number of old trades requested.
    :param include_old: (bool) Retrieve trades that more than 7 days old.
    :return: (dict) Message to be sent into the websocket.
    """

    data = sanitize(currency=currency, kind=kind, count=count, include_old=include_old)

    # Build basic message
    msg = message(method=TRADING_USER_TRADES_BY_CURRENCY)
    params = {key: value for (key, value) in data.items()}
    return add_params_to_message(params, msg)


def user_trades_by_instrument(instrument: str, count: int = None, include_old: bool = None):
    """
    Request all open user_trades for a given instrument.
    :param instrument: (str) delta instrument's name
    :param count: (int) The number of old trades requested.
    :param include_old: (bool) Retrieve trades that more than 7 days old.
    :return: (dict) Message to be sent into the websocket.
    """

    data = sanitize(instrument=instrument, count=count, include_old=include_old)

    # Build basic message
    msg = message(method=TRADING_USER_TRADES_BY_INSTRUMENT)
    params = {key: value for (key, value) in data.items()}
    return add_params_to_message(params, msg)


def order_status(order_id: str):
    """
    Generates a request for qn estimated margins for a trade.
    :param order_id: (str) delta order id
    :return: (dict) Message to be sent into the websocket.
    """

    data = sanitize(order_id=order_id)

    # Build basic message
    msg = message(method=TRADING_COMPUTE_MARGIN)
    params = {key: value for (key, value) in data.items()}
    return add_params_to_message(params, msg)


# ######################################################################
# ASSERTIONS
# ######################################################################


def assert_limit_order_coherence(order_type, limit_price=None):
    # Check 1: Limit orders
    # If limit_order type, the limit price should be provided
    if order_type == ORDER_TYPE.LIMIT.value.lower() or order_type == ORDER_TYPE.STOP_LIMIT.value.lower():
        if not limit_price:
            raise KeyError("Limit price must be provided for limit or stop-limit orders.")

    # Check 2: (reverse)
    # If limit price provided, order should be limit order
    if limit_price:
        if order_type != ORDER_TYPE.LIMIT.value.lower() and order_type != ORDER_TYPE.STOP_LIMIT.value.lower():
            raise KeyError(f"Incoherent order. Limit price provided, but order type is {order_type}.")


def assert_stop_order_coherence(order_type, buy_order: bool, data: Dict,
                                stop_price=None, limit_price=None):
    # Check 1: Stop-containers orders
    # If stop_order type, the stop price should be provided
    if order_type == ORDER_TYPE.STOP_MARKET.value.lower():
        if not stop_price:
            raise KeyError("Stop price must be provided for stop-containers orders.")

    # Check 2: Stop-limit orders
    # If stop_order type with limit, the stop price should be provided and below limit
    elif order_type == ORDER_TYPE.STOP_LIMIT.value.lower():
        if not stop_price:
            raise KeyError("Stop price must be provided for stop-limit orders.")

        if not limit_price:
            raise KeyError("Limit price must be provided for stop-limit orders.")

        if buy_order and (stop_price < limit_price):
            raise ValueError("Stop price must be higher than limit price for buy orders.")

        if not buy_order and (stop_price > limit_price):
            raise ValueError("Stop price must be lower than limit price for sell orders.")

    # This is not a stop-limit nor a stop-containers order, no trigger required
    else:
        if "trigger" in data:
            del data["trigger"]


def assert_cancellation_order_type(order_type):
    # Check 1: Order type must be either limit or stop. Default to 'all'
    if order_type == ORDER_TYPE.MARKET.value.lower():
        raise KeyError(f"Incoherent cancellation order type ({order_type}).")
