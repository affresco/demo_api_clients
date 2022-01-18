from typing import List
from .common import message, add_params_to_message
from ..support.endpoints import *


# ######################################################################
# HEARTBEAT
# ######################################################################

def set_heartbeat_message():
    msg = message(method=SESSION_SET_HEARTBEAT)
    return add_params_to_message(kvp_dict={"interval": 30}, message=msg)


def disable_heartbeat_message():
    msg = message(method=SESSION_SET_HEARTBEAT)
    return add_params_to_message(kvp_dict={}, message=msg)

def test_heartbeat_request_message():
    msg = message(method=SESSION_TEST)
    return add_params_to_message(kvp_dict={}, message=msg)

# ######################################################################
# TIME
# ######################################################################

def get_time():
    msg = message(method=SESSION_GET_TIME)
    return add_params_to_message(kvp_dict={}, message=msg)


# ######################################################################
# TESTS
# ######################################################################

def test_no_exception():
    msg = message(method=SESSION_TEST)
    return add_params_to_message(kvp_dict={}, message=msg)


def test_with_exception():
    msg = message(method=SESSION_TEST)
    return add_params_to_message(kvp_dict={"expected_result": "exception"}, message=msg)


# ######################################################################
# SUBSCRIPTION
# ######################################################################

def subscription_message(channels):
    if not isinstance(channels, List):
        channels = [channels]
    msg = message(method=METHOD_SUBSCRIBE)
    params = {"channels": channels}
    return add_params_to_message(params, msg)


def unsubscription_message(channels):
    if not isinstance(channels, List):
        channels = [channels]

    msg = message(method=METHOD_UNSUBSCRIBE)
    params = {"channels": channels}
    return add_params_to_message(params, msg)

def private_subscription_message(channels):
    if not isinstance(channels, List):
        channels = [channels]
    msg = message(method=METHOD_PRIVATE_SUBSCRIBE)
    params = {"channels": channels}
    return add_params_to_message(params, msg)


def private_unsubscription_message(channels):
    if not isinstance(channels, List):
        channels = [channels]

    msg = message(method=METHOD_PRIVATE_UNSUBSCRIBE)
    params = {"channels": channels}
    return add_params_to_message(params, msg)


# ######################################################################
# LOGIN
# ######################################################################

def login_message(key, secret):
    msg = message(method=SESSION_LOGIN)
    msg["params"] = {}
    credentials = {"grant_type": "client_credentials",
                   "client_id": key,
                   "client_secret": secret}
    msg["params"] = {**msg["params"], **credentials}
    return add_params_to_message({}, msg)


# ######################################################################
# CANCEL ON DISCONNECT
# ######################################################################

def enable_cancel_on_disconnect(key, secret):
    msg = message(method=SESSION_ENABLE_CANCEL_ON_DISCONNECT)
    return add_params_to_message({}, msg)


def disable_cancel_on_disconnect(key, secret):
    msg = message(method=SESSION_DISABLE_CANCEL_ON_DISCONNECT)
    return add_params_to_message({}, msg)
