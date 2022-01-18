from .common import message, add_params_to_message

from ..support.endpoints import *
from ..support.sanitizers import *
from ..support.identification import message_id

from ..messages.common import build_channel
from ..support.types import INTERVAL, PUBLIC_CHANNELS

from utilities.marshal import to_list
from deribit.standards import DEFAULT_KINDS, DEFAULT_CURRENCIES


# ######################################################################
# REQUESTS
# ######################################################################

def request_instruments(currency: str = None, kind: str = None, expired=None):
    """
    Make messages for delta
    :param currency:
    :param kind:
    :param expired:
    :return:
    """

    # Defaults
    currency = currency or DEFAULT_CURRENCIES
    kind = kind or DEFAULT_KINDS

    if expired is None:
        expired = [True, False]

    # Marshal
    currency = to_list(currency)
    kind = to_list(kind)
    expired = to_list(expired)

    output = []
    for k in kind:
        for ccy in currency:
            for ex in expired:
                output.append(__get_instruments(ccy, k, ex))
    return output


def __get_instruments(currency: str, kind: str, expired: bool):
    """
    Create a message to get all positions for a given currency on delta.
    :param currency: String symbol (e.g. 'BTC' or 'ETH')
    :param kind: Type of contract (either 'future' or 'option')
    :return: Message (dict)
    """

    # Sanitize input arguments
    data = sanitize(currency=currency, kind=kind)

    # Build basic message
    msg = message(method=DATA_GET_INSTRUMENTS)
    params = {"currency": data["currency"], "kind": data["kind"], "expired": str(expired).lower()}
    return add_params_to_message(params, msg)


def request_book_summary_by_currency(currency: str):
    """

    :param currency:
    :return:
    """

    # Sanitize input arguments
    data = sanitize(currency=currency)

    # Get basic method call
    msg = message(method=DATA_BOOK_SUMMARY_BY_CURRENCY)

    # Add parameters
    params = {"currency": data["currency"]}
    return add_params_to_message(params, msg)


def request_book_summary_by_instrument(instrument: str):
    """

    :param instrument:
    :return:
    """

    # Sanitize input arguments
    data = sanitize(instrument=instrument)

    # Get basic method call
    msg = message(method=DATA_BOOK_SUMMARY_BY_INSTRUMENT)

    # Add parameters
    params = {"instrument_name": data["instrument"]}
    return add_params_to_message(params, msg)


def request_orderbook(instrument: str, depth: int = None):
    """
    :param instrument:
    :param depth:
    :return:
    """
    # Sanitize input arguments
    data = sanitize(instrument=instrument, depth=depth)

    # Get basic method call
    msg = message(method=DATA_GET_ORDER_BOOK)

    # Add parameters
    params = {"instrument_name": data["instrument"], "depth": data["depth"]}
    return add_params_to_message(params, msg)


def request_orderbooks(instruments: list, depth: int = None):
    """

    :param instruments:
    :param depth:
    :return:
    """
    messages = []
    for ins in instruments:
        messages.append(request_orderbook(ins, depth))
    return messages


def request_currencies():
    """

    :return:
    """
    msg = message(method=DATA_CURRENCIES)
    return add_params_to_message({}, msg)


def request_quotes(instruments: list):
    """

    :param instruments:
    :return:
    """
    instruments = instruments if isinstance(instruments, list) else [instruments]
    return request_orderbooks(instruments=instruments, depth=1)


def request_index(currency: str):
    """

    :param currency:
    :return:
    """
    # Sanitize input arguments
    data = sanitize(currency=currency)
    params = {"currency": data["currency"]}
    msg = message(method=DATA_INDEX)
    return add_params_to_message(params, msg)


def request_all_trades(data, chunk_size=250):
    """

    :param data:
    :param chunk_size:
    :return:
    """

    import random
    import string
    characters_set = string.ascii_letters + string.digits

    def __message(instrument_name, start_seq, end_seq):
        msg = {'jsonrpc': '2.0',
               'id': ''.join(random.choice(characters_set) for _ in range(6)),
               'method': 'public/get_last_trades_by_instrument',
               'params': {"instrument_name": instrument_name,
                          "include_old": True,
                          "start_seq": start_seq,
                          "end_seq": end_seq,
                          "count": end_seq - start_seq}}
        return msg

    parsed_data = []
    if not isinstance(data, list):
        data = [data]

    for blob in data:
        try:
            parsed_data.append({"instrument": blob["result"]["trades"][0]["instrument_name"],
                                "end_seq": blob["result"]["trades"][0]["trade_seq"]})
        except:
            pass

    messages = []

    for blob in parsed_data:

        end_seq = blob["end_seq"]
        instrument = blob["instrument"]

        chunks = int(math.ceil(end_seq / chunk_size))
        start_seqs = [chunk_size * i for i in range(chunks)]
        end_seqs = [min((chunk_size * i) - 1, end_seq) for i in range(1, chunks + 1)]

        messages = [__message(instrument_name=instrument,
                              start_seq=start_seqs[i],
                              end_seq=end_seqs[i]) for i in range(chunks)]

    return messages


def request_trades(instruments: list,
                   count: int = None,
                   include_old: bool = True,
                   start_seq: int = None,
                   end_seq: int = None):
    """

    :param instruments:
    :param count:
    :param include_old:
    :param start_seq:
    :param end_seq:
    :return:
    """

    def __to_list(x):
        if not isinstance(x, list):
            return [x]
        return instruments

    def __count(data):
        if "count" in data:
            if not data["count"]:
                data["count"] = 1000
            else:
                data["count"] = min(1000, data["count"])
        return data

    def __start_seq(data):
        if not data["start_seq"]:
            del data["start_seq"]
        else:
            data["start_seq"] = max(1, data["start_seq"])
        return data

    def __end_seq(data):
        if not data["end_seq"]:
            if "start_seq" not in data:
                del data["end_seq"]
            else:
                data["end_seq"] = data["start_seq"] + data["count"]
        else:
            if "start_seq" not in data:
                data["start_seq"] = max(data["end_seq"] - data["count"], 1)
        return data

    def __reset_count(data):
        if ("start_seq" in data) and ("end_seq" in data):
            data["count"] = min(1000, data["end_seq"] - data["start_seq"])
        return data

    def __ensure_coherence(data):
        return __reset_count(__end_seq(__start_seq(__count(data))))

    def __message(instrument_name, data):
        msg = message(method=DATA_LAST_TRADES_BY_INSTRUMENT)
        cmn_params = {key: value for (key, value) in data.items()}
        return add_params_to_message({**cmn_params, **{"instrument_name": instrument_name}}, msg)

    common_data = sanitize(count=count,
                           include_old=include_old,
                           start_seq=start_seq,
                           end_seq=end_seq)

    common_data = __ensure_coherence(common_data)
    instruments_ = [sanitize(instrument=x)["instrument"] for x in __to_list(instruments)]
    messages = [__message(instrument_name=x, data=common_data) for x in instruments_]
    return messages


def request_last_trades_by_instrument(instrument: str,
                                      count: int = None,
                                      include_old: bool = True,
                                      start_seq: int = None,
                                      end_seq: int = None):
    """
    Request all open user_trades for a given instrument.
    :param instrument: (str) delta instrument's name
    :param count: (int) The number of old trades requested.
    :param include_old: (bool) Retrieve trades that more than 7 days old.
    :param start_seq: (int) Retrieve trades from that trade seq (unique per instrument)
    :param end_seq: (int) Retrieve trades up to that trade seq (unique per instrument)
    :return: (dict) Message to be sent into the websocket.
    """

    data = sanitize(instrument_name=instrument,
                    count=count,
                    include_old=include_old,
                    start_seq=start_seq,
                    end_seq=end_seq)

    # Enforcing count (if present)
    if "count" in data:
        if not data["count"]:
            data["count"] = 1000
        else:
            data["count"] = min(1000, data["count"])

    # Enforcing start seq (if present)
    if not data["start_seq"]:
        del data["start_seq"]
    else:
        data["start_seq"] = max(1, data["start_seq"])

    # Enforcing coherence with start_seq
    if not data["end_seq"]:
        if "start_seq" not in data:
            del data["end_seq"]
        else:
            data["end_seq"] = data["start_seq"] + data["count"]

    else:
        if "start_seq" not in data:
            data["start_seq"] = max(data["end_seq"] - data["count"], 1)

    if ("start_seq" in data) and ("end_seq" in data):
        data["count"] = min(1000, data["end_seq"] - data["start_seq"])

    # Build message
    msg = message(method=DATA_LAST_TRADES_BY_INSTRUMENT)
    params = {key: value for (key, value) in data.items()}
    return add_params_to_message(params, msg)


# ######################################################################
# SUBSCRIPTIONS
# ######################################################################

def subscribe_orderbooks(instrument: str,
                         interval: int = DEFAULT_INTERVAL,
                         group: int = None,
                         depth: int = None):
    """

    :param instrument:
    :param interval:
    :param group:
    :param depth:
    :return:
    """
    # Sanitize input arguments
    data = sanitize(instrument=instrument, interval=interval,
                    group=group, depth=depth)

    # WARNING: For orderbook modification, the only supported
    # interval is 100ms.
    channel = build_channel(header=PUBLIC_CHANNELS.ORDERBOOK_UPDATES.value,
                            instrument=data["instrument"],
                            group=data["group"],
                            depth=data["depth"],
                            interval=INTERVAL.STANDARD.value)
    return channel


def subscribe_trades(instrument: str, interval: int = None):
    """

    :param instrument:
    :param interval:
    :return:
    """
    # Sanitize input arguments
    data = sanitize(instrument=instrument, interval=interval)

    # Get (option_clean) channel name
    channel = build_channel(header=PUBLIC_CHANNELS.TRADES.value,
                            instrument=data["instrument"],
                            interval=data["interval"])
    return channel


def subscribe_quotes(instrument: str):
    """

    :param instrument:
    :return:
    """
    # Sanitize input arguments
    data = sanitize(instrument=instrument)

    # Get (option_clean) channel name
    channel = build_channel(header=PUBLIC_CHANNELS.QUOTES.value,
                            instrument=data["instrument"])
    return channel
