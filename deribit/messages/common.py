from typing import List
from ..support.identification import message_id
from ..support.networking import *


# ######################################################################
# PUBLIC
# ######################################################################

@property
def empty_message():
    """
    Creates a basic message for the delta API (JSON/RPC).
    :return: Message (dict)
    """
    return message()


def message(method=None, msg=None):
    """
    Creates a message for the delta API.
    :param method: Route targeted.
    :param msg: Pre-existing message (dict) to be modified and returned.
    :return: Message (dict)
    """
    if not msg:
        msg = add_message_id(message=add_rpc_protocol({}))

    if not method:
        return msg

    return add_method(method, msg)


def add_method(method, message=None):
    """
    Add a route to a message.
    :param method: Route targeted.
    :param message: Pre-existing message (dict) to be modified and returned.
    :return: Message (dict)
    """
    message[REQ_METHOD] = method
    return message


def add_params_to_message(kvp_dict, message):
    """
    Add queries parameters to a message.
    :param kvp_dict:
    :param message: Pre-existing message (dict) to be modified and returned.
    :return: Message (dict)
    """
    if REQ_PARAMS not in message:
        message[REQ_PARAMS] = {}
    for k in kvp_dict:
        if kvp_dict[k]:
            message[REQ_PARAMS][k] = kvp_dict[k]
    return message


def add_channels_to_message(channels: List, message):
    """
    Add channels (for subscription) parameters to a message.
    :param channels: Channel targeted (e.g. 'BOOK.BTC-PERPETUAL.100.ms').
    :param message: Pre-existing message (dict) to be modified and returned.
    :return: Message (dict)
    """
    if not isinstance(channels, List):
        channels = [channels]
    if REQ_PARAMS not in message:
        message[REQ_PARAMS] = {}
    channels[REQ_PARAMS][CHANNELS] = channels
    return channels


# ##################################################################
# PRIVATE METHODS
# ##################################################################

def add_rpc_protocol(message):
    """
    Add the current delta RPC protocol to the message.
    :param message: Pre-existing message (dict) to be modified and returned.
    :return: Message (dict)
    """
    message[PROTOCOL] = PROTOCOL_VERSION
    return message


def add_message_id(message, id=None):
    """
    Add a alpha ID to the message.
    :param message: Pre-existing message (dict) to be modified and returned.
    :param id: String representing the alpha ID. Will be returned along in the response.
    :return: Message (dict)
    """
    id_ = id
    if not id_:
        id_ = message_id()
    message["id"] = id_
    return message


# ######################################################################
# METHODS
# ######################################################################

def build_channel(header, instrument=None, interval=None, group=None, depth=None):
    content = {"channel": header,
               "instrument": instrument,
               "group": str(group),
               "depth": str(depth),
               "interval": str(interval)}

    if not instrument:
        del content["instrument"]

    if not interval:
        del content["interval"]

    if not group:
        del content["group"]

    if not depth:
        del content["depth"]

    return '.'.join([content[k] for k in content])