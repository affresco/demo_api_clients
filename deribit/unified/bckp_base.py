# Core
import time
import logging
import threading
from abc import ABC
import datetime as dt

# External frameworks
import websocket
from blinker import Signal
from websocket._exceptions import WebSocketConnectionClosedException

# Local apps
from utilities import json
from utilities.id import generate_id
from deribit.messages import session

# ####################################################################
# CONSTANTS
# ####################################################################

MAX_STARTUP_TIME = 2.0
REQUEST_MAX_RETRIES = 10
CHECK_INTERVAL = 0.00001
STARTUP_SCALING = 10
REQUEST_TIMEOUT = 5.0


PING_INTERVAL = 10
PING_TIMEOUT = 5

# ####################################################################
# LOGGING
# ####################################################################

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ####################################################################
# EVENTS
# ####################################################################

# Events
EVENT_WS_PING = Signal(f"WEBSOCKET-PING")
EVENT_WS_PONG = Signal(f"WEBSOCKET-PONG")
EVENT_WS_ERROR = Signal(f"EVENT-WS-ERROR")
EVENT_WS_OPEN = Signal(f"EVENT-WS-OPEN")
EVENT_WS_LOGIN = Signal(f"EVENT-WS-LOGIN")
EVENT_WS_CLOSE = Signal(f"EVENT-WS-CLOSE")


# ####################################################################
# CLIENT (FOR PUNCTUAL REQUESTS)
# ####################################################################

class UnifiedClient(ABC):

    # ##################################################################
    # INIT
    # ##################################################################

    def __init__(self,
                 url,                                                   # Base url for connection
                 key=None, secret=None,                                 # Connection using credentials
                 access_token=None, refresh_token=None, expiry=None,    # Connection using tokens
                 name=None,                                             # Name of this connection
                 callback=None):                                        # Default callback (callable)

        # Default callback (for subscriptions only)
        self._callback = callback

        # Base url
        self.__url = url

        # Credentials
        self.__key = key
        self.__secret = secret

        # Bool: ok to use credentials
        self.__authenticate_with_credentials = bool(key and secret)

        # Tokens: stored at login, but not used... @ TODO
        self.__access_token = access_token
        self.__refresh_token = refresh_token
        self.__token_expiry = expiry

        # Bool: ok to use token
        self.__authenticate_with_token = bool(access_token)

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

    # ##################################################################
    # DESTRUCTION
    # ##################################################################

    def __del__(self):
        self._is_closing = True

    # ##################################################################
    # PROPERTIES
    # ##################################################################

    @property
    def ws(self):
        if not self.__ws:
            self.maybe_reconnect()
        return self.__ws

    # ##################################################################
    # WEBSOCKET BASIC OPERATIONS
    # ##################################################################

    def run_forever_on_thread(self, ws, startup_delay):

        # Trying to implement heartbeat
        kwargs = {"ping_interval": PING_INTERVAL, "ping_timeout": PING_TIMEOUT}
        th = threading.Thread(target=ws.run_forever, kwargs=kwargs)

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

    def send_request(self, message, callback=None):
        msg_cb = [(message, callback)]
        return self.send_multiple_requests(msg_cb)

    def send_multiple_requests(self, messages_with_callbacks, retry=0):
        try:
            if retry > REQUEST_MAX_RETRIES:
                raise ConnectionAbortedError("Maximum number of retries reached.")

            # Look for broken connections
            self.maybe_reconnect()

            gentle_delay = 0.05 if len(messages_with_callbacks) > 50 else 0.0

            counter = 0
            while not self._secured_connection and counter < MAX_STARTUP_TIME:
                time.sleep(CHECK_INTERVAL)
                counter += CHECK_INTERVAL

            # Send each message
            waiting_ids = []
            for msg_tuple in messages_with_callbacks:

                msg, cb = msg_tuple[0], msg_tuple[1]

                id_ = msg["id"]
                self.ws.send(json.dumps(msg))
                self._sent_messages[id_] = msg

                if cb:
                    self._sent_messages_callbacks[id_] = cb
                else:
                    waiting_ids.append(id_)

                time.sleep(gentle_delay)

            # If not callback provided,
            # wait for the answer to arrive
            if len(waiting_ids) > 0:
                return self.__wait_blocking(ids=waiting_ids)

        except WebSocketConnectionClosedException:
            self.maybe_reconnect()
            time.sleep(0.01)
            retry += 1
            return self.send_multiple_requests(messages_with_callbacks=messages_with_callbacks,
                                               retry=retry)

    def __wait_blocking(self, ids):

        ids = ids if isinstance(ids, list) else [ids]
        total_number_of_ids = len(ids)

        waiting_time = 0.0
        result, queue = {}, self._answers_received

        while waiting_time < REQUEST_TIMEOUT:

            # If the number of answers is not even the length of our
            # messages, leave it be...
            if len(self._answers_received) >= total_number_of_ids:

                result = {id: queue[id] for id in ids if id in queue}

                if len(result) == total_number_of_ids:
                    break

            # Some answers are missing, wait a bit...
            time.sleep(CHECK_INTERVAL)
            waiting_time += CHECK_INTERVAL

        # Clean up
        for id in ids:
            try:
                del self._answers_received[id]
                del self._sent_messages[id]
            except:
                pass

        # Return
        return list(result.values())

    # ##################################################################
    # MESSAGE HANDLER
    # ##################################################################

    def _on_message(self, ws, message):

        # Parse the message to python data
        message = json.loads(message)

        print(message)

        # This is a real message:
        # propagate to the user's callback
        id = message.get("id", False)
        if id:
            return self._on_message_with_id(message, id)
        else:
            return self._on_message_without_id(message)

    def _on_message_with_id(self, message, id):

        # Add to acknowledged messages
        self._answers_received[id] = message

        # Invoke the callback if there is one, else do nothing
        # this assumes that if there is no callback, the method
        # generating the request is waiting for the reply
        if id in self._sent_messages_callbacks:
            # Grab the callback
            cb = self._sent_messages_callbacks[id]

            # Clean up
            del self._sent_messages[id]
            del self._sent_messages_callbacks[id]
            del self._answers_received[id]

            # Invoke
            return cb(message)

    def _on_message_without_id(self, message):

        method = message.get("method", None)

        # This messages comes from an existing
        # channel subscription, use provided callback
        if method == "subscription":
            return self.on_subscription(message)

        # This is a heartbeat message, NOT to be propagated
        # to the callback provided by the user
        if method == "heartbeat":
            return self._on_heartbeat(message)

        # Message not handled, log this as an error
        # This is NOT supposed to happen
        logger.error(f"Got unexpected message: {message}")

    def on_subscription(self, message):
        print(".")
        return self._callback(message)

    # ##################################################################
    # ERROR HANDLER
    # ##################################################################

    def _on_error(self, ws, message):

        # Warn the system about the event
        EVENT_WS_ERROR.send()

        # Log the event
        logger.error(message)

    # ##################################################################
    # OPEN HANDLER
    # ##################################################################

    def _on_open(self, ws):

        # Warn the system about the event
        EVENT_WS_OPEN.send()

        # Log the event
        logger.info("Opening web socket connection.")

        # The client has been provided with a username and password
        # logging in this way will trigger the retrieval of the tokens
        # which will later be used.
        if self.__authenticate_with_credentials:
            # Create message with credentials to retrieve the oauth token
            credentials = session.login_message(key=self.__key, secret=self.__secret)
            self.__send_preliminary_request(credentials, credentials["id"], self._on_login)

    def set_tokens(self, message):

        result = message.get("result", None)

        # Make sure that there is a valid content
        if not result:
            EVENT_WS_ERROR.send()
            raise NotImplementedError()

        # Extract relevant token information
        access_token = result.get("access_token", False)
        refresh_token = result.get("refresh_token", False)

        # Validate that we have at least an access token
        if not access_token or not refresh_token:
            EVENT_WS_ERROR.send()
            raise NotImplementedError("Invalid login reply, unable to extract token information.")
        else:
            self.__access_token = access_token
            self.__refresh_token = refresh_token
            self.__authenticate_with_token = True

        # Compute token expiry
        expiry_seconds = result.get("expires_in", False)
        expiry = expiry_seconds + dt.datetime.utcnow().timestamp()

        # Validate that we have at least an access token
        if not access_token or not refresh_token:
            EVENT_WS_ERROR.send()
            raise NotImplementedError("Invalid token expiry provided.")
        else:
            self.__token_expiry = expiry

    def _on_login(self, message):

        if "error" in message:
            EVENT_WS_ERROR.send()
            raise NotImplementedError()

        self.set_tokens(message)

        self._secured_connection = True
        logger.info("Web socket opened.")

        self._disconnect_back_off = 0.25

        # Enable heartbeat
        heartbeat_msg = session.set_heartbeat_message()
        self.__send_preliminary_request(heartbeat_msg, heartbeat_msg["id"], self._on_heartbeat)

    def __send_preliminary_request(self, message, id, callback):
        self._sent_messages[id] = message
        self._sent_messages_callbacks[id] = callback
        self.ws.send(json.dumps(message))

    # ##################################################################
    # CLOSE HANDLER
    # ##################################################################

    def _on_close(self, ws):
        print("Socket closing.")

        # Was supposed to happen
        if self._is_closing:
            try:
                ws.retire()
                EVENT_WS_CLOSE.send()
            except:
                pass
        # Not expected
        else:

            # Warn system of a problem.
            EVENT_WS_ERROR.send()

            # Log it
            logger.warning("Connection ended unexpectedly. Reconnecting to web socket server.")

            # Delete the actual socket
            self.__ws = None

            # Back off:
            self._disconnect_back_off *= 2
            time.sleep(min(10.0, self._disconnect_back_off))

            # Reconnect
            self.maybe_reconnect()

    # ##################################################################
    # HEARTBEAT HANDLERS
    # ##################################################################

    def _on_ping(self, ws, message, *args, **kwargs):
        EVENT_WS_PING.send()

    def _on_pong(self, msg=None, *args, **kwargs):
        EVENT_WS_PONG.send()

    def _on_heartbeat(self, message, *arg, **kwargs):
        params = message.get("params")
        type_ = params.get("type")

        # External provider sending us a heartbeat
        # Ignore for now
        if type_ == "heartbeat":
            return

        # Exchange asking us for a reply
        # to their heartbeat, must hit the 'test' api endpoint
        if type_ == "test_request":
            reply_msg = session.test_heartbeat_request_message()
            return self.send_request(reply_msg, callback=self._on_heartbeat)
