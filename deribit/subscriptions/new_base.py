# Core
import time
import logging
import threading
from abc import ABC

# External frameworks
import websocket
from blinker import Signal

# Our repo
from utilities import json
from deribit.messages import session
from utilities.id import generate_id

# ####################################################################
# LOGGING
# ####################################################################

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ####################################################################
# CONSTANTS
# ####################################################################

MAX_STARTUP_TIME = 2.0
REQUEST_MAX_RETRIES = 10
CHECK_INTERVAL = 0.00001
STARTUP_SCALING = 10
REQUEST_TIMEOUT = 5.0


# ####################################################################
# DELTA CLIENT FOR PUNCTUAL REQUEST VIA HTTP GET
# ####################################################################

class WebsocketClient(ABC):

    # ##################################################################
    # INIT
    # ##################################################################

    def __init__(self, url, key, secret, name):

        self._msg_counter = 0

        # Base uri
        self.__url = url

        # Credentials
        self.__key = key
        self.__secret = secret

        # Name for events
        self._name = name or generate_id(4).upper()

        # Time to establish the initial connection
        self._startup_delay = 10  # in milliseconds

        # Properties
        self._is_closing = False

        # Messages: information about SENT messages
        self._sent_messages = {}
        self._sent_messages_callbacks = {}

        # Messages: information about RECEIVED messages
        self._answers_received = {}

        # Startup precautions
        self._secured_connection = False

        # Last unexpected disconnect
        self._disconnect_back_off = 0.25

        # Events
        self._event_on_pong = Signal(f"DELTA-PONG-RECEIVED-{self._name}")

        # Handle: on message
        def on_message(ws, message):
            return self._on_message(ws, message)

        self.on_message = on_message

        # Handle: on error
        def on_error(ws, message):
            return self._on_error(ws, message)

        self.on_error = on_error

        # Handle: on open
        def on_open(ws):
            return self._on_open(ws)

        self.on_open = on_open

        # Handle: on close
        def on_close(ws):
            return self._on_close(ws)

        self.on_close = on_close

        # Handle: on ping
        def on_ping(ws, *args, **kwargs):
            return self._on_ping(ws, *args, **kwargs)

        self.on_ping = on_ping

        # Handle: on pong
        def on_pong(ws, *args, **kwargs):
            return self._on_pong(ws, *args, **kwargs)

        self.on_pong = on_pong

        # Websocket
        self.__ws = None

    def __del__(self):
        self._is_closing = True

    # ##################################################################
    # EVENT HANDLERS
    # ##################################################################

    def _on_message(self, ws, message):

        # Parse the message to python data
        message = json.loads(message)

        print("**********************************************")
        print(message)

        print(message)

        # This is a heartbeat message, NOT to be propagated
        # to the callback provided by the user
        if self.is_heartbeat(message):
            return self.on_heartbeat(message)

        # This is a real message:
        # propagate to the user's callback
        return self.acknowledge(message)

    def _on_error(self, ws, message):
        logger.error(message)

    def _on_open(self, ws):

        logger.info("Opening web socket connection.")

        credentials = session.login_message(key=self.__key, secret=self.__secret)
        id_ = credentials["id"]

        self._sent_messages[id_] = credentials
        self._sent_messages_callbacks[id_] = self._on_login

        ws.send(json.dumps(credentials))

    def _on_login(self, message):

        if not "error" in message:
            self._secured_connection = True
            print("Web socket opened.")

            self._disconnect_back_off = 0.25

            # Enable heartbeat
            enable_heartbeat_msg = session.set_heartbeat_message()

            id_ = enable_heartbeat_msg["id"]
            self._sent_messages[id_] = enable_heartbeat_msg
            self._sent_messages_callbacks[id_] = self.on_heartbeat

            self.ws.send(json.dumps(enable_heartbeat_msg))


        else:
            pass

    def _on_close(self, ws):
        print("Socket closed.")

        # Was supposed to happen
        if self._is_closing:
            try:
                ws.retire()
            except:
                pass
        # Not expected
        else:
            logger.warning("Connection ended unexpectedly. Reconnecting to web socket server.")
            self.__ws = None

            # Back off:
            self._disconnect_back_off *= 2
            time.sleep(min(10.0, self._disconnect_back_off))

            self.maybe_reconnect()

    def _on_ping(self, ws, message, *args, **kwargs):
        print(f"On Ping: {message}")

    def _on_pong(self, *args, **kwargs):
        print("sending Pong event")
        self._event_on_pong.send()

    def on_heartbeat(self, message, *arg, **kwargs):
        params = message.get("params")
        type_ = params.get("type")

        # External provider sending us a heartbeat
        # Ignore for now
        if type_ == "heartbeat":
            return

        # Exchange asking us for a reply
        # to their heartbeat, must hit the 'test' api endpoint
        if type_ == "test_request":

            hb_resp_msg = session.test_heartbeat_request_message()
            # return self.ws.send(json.dumps(hb_resp_msg))
            self.ws.send(json.dumps(hb_resp_msg))

            # FIXME THIS IS TEST, REMOVE THIS
            test_sub_msg = session.subscription_message(channels="quote.BTC-25DEC20")
            self.send_request(test_sub_msg, callback=self.just_print)

    def just_print(self, msg):
        self._msg_counter += 1
        if self._msg_counter == 10:
            from deribit.messages import mkt_data
            test_sub_msg = mkt_data.request_currencies()
            self.send_request(test_sub_msg, callback=self.just_print)

        elif self._msg_counter > 15:
            test_unsub_msg = session.unsubscription_message(channels="quote.BTC-25DEC20")
            self.send_request(test_unsub_msg, callback=self.just_print)

        print(msg)

    # ##################################################################
    # RUN
    # ##################################################################

    def run_forever_on_thread(self, ws, startup_delay):

        # Trying to implement heartbeat
        kwargs = {"ping_interval": 10, "ping_timeout": 3}
        th = threading.Thread(target=ws.run_forever, kwargs=kwargs)

        # This is the true version
        # kwargs = {"ping_interval": 30, "ping_timeout": 15}
        # th = threading.Thread(target=ws.run_forever, kwargs=kwargs)

        th.start()
        time.sleep(max(0.025, startup_delay / 1000.0))

    def maybe_reconnect(self):
        if not self.__ws:
            ws = websocket.WebSocketApp(self.__url,
                                        on_open=self.on_open,
                                        on_message=self.on_message,
                                        on_error=self.on_error,
                                        on_close=self.on_close,
                                        on_ping=self.on_ping,
                                        on_pong=self.on_pong)
            # Set locally
            self.__ws = ws
            self.run_forever_on_thread(ws, startup_delay=self._startup_delay)

    # ##################################################################
    # WEBSOCKET BASIC OPERATIONS
    # ##################################################################

    @property
    def ws(self):
        if not self.__ws:
            self.maybe_reconnect()
        return self.__ws

    def send_request(self, message, callback=None):
        msg_cb = [(message, callback)]
        return self.send_multiple_requests(msg_cb)

    # ##################################################################
    # ABSTRACT METHODS
    # ##################################################################

    def send_multiple_requests(self, *args, **kwargs):
        raise NotImplementedError()

    def acknowledge(self, *args, **kwargs):
        raise NotImplementedError()

    # ##################################################################
    # HEARTBEAT MESSAGE HANDLING
    # ##################################################################

    def is_heartbeat(self, message):

        if message.get("method", False):
            return False

        params = message.get("params", False)
        if params:
            return True
        return False

