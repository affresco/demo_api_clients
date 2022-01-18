# Frameworks
import time

# Exceptions from Websocket package
from websocket._exceptions import WebSocketConnectionClosedException

# Utilities
from utilities import json
from utilities import marshal

# Local app
from deribit.messages import session

# TODO This FILE SHOULD BE ELSEWHERE
from deribit.subscriptions.new_base import WebsocketClient

# ####################################################################
# CONSTANTS
# ####################################################################

MAX_STARTUP_TIME = 2.0
REQUEST_MAX_RETRIES = 10
CHECK_INTERVAL = 0.00001
STARTUP_SCALING = 10
REQUEST_TIMEOUT = 5.0


# ####################################################################
# CLIENT (FOR SUBSCRIBING TO DATA STREAMS)
# ####################################################################

class SubscriptionClient(WebsocketClient):

    def __init__(self, url, key, secret, callback, name):
        self._callback = callback
        super().__init__(url, key, secret, name=name.upper())

    # ##################################################################
    # WEBSOCKET BASIC OPERATIONS
    # ##################################################################

    def send_request(self, message, callback=None):
        return self.send_multiple_requests([message])


    def send_multiple_requests(self, messages, retry=0):
        try:
            if retry > REQUEST_MAX_RETRIES:
                raise ConnectionAbortedError("Maximum number of retries reached.")

            # Look for broken connections
            self.maybe_reconnect()

            gentle_delay = 0.01 if len(messages) > 50 else 0.0

            counter = 0
            while not self._secured_connection and counter < MAX_STARTUP_TIME:
                time.sleep(CHECK_INTERVAL)
                counter += CHECK_INTERVAL

            # Send each message
            for msg in messages:
                # Get the message identifier
                id_ = msg["id"]

                # Send the message thru the websocket
                self.ws.send(json.dumps(msg))

                # Add the message to the 'sent' list
                self._sent_messages[id_] = msg

                # Add a little time in between messages
                # to help external provider handle the load
                time.sleep(gentle_delay)

        except WebSocketConnectionClosedException:
            self.maybe_reconnect()
            time.sleep(0.01)
            retry += 1
            return self.send_multiple_requests(messages=messages, retry=retry)

        # ##################################################################
        # EVENT HANDLERS
        # ##################################################################

    def acknowledge(self, message):

        # Our acknowledgement messages contain our ID
        msg_id = message.get("id", None)

        # Assumes this is a CONFIRMATION message,
        # meaning that our request to (un-) subscribe
        # has been acknowledge by the external provider
        if msg_id in self._sent_messages_callbacks:

            # Message monitoring: clean up
            del self._sent_messages[msg_id]
            del self._answers_received[msg_id]
            return

        else:
            return self.monitored_callback(message)

    def monitored_callback(self, message):
        try:
            return self._callback(message)
        except:
            print("Callback invocation failure.")

    # ##################################################################
    # SUBSCRIBE
    # ##################################################################

    def subscribe(self, channels: list):
        channels = marshal.to_list(channels)
        messages = session.subscription_message(channels)
        return self.send_request(messages)

    def unsubscribe(self, channels: list):
        channels = marshal.to_list(channels)
        messages = session.unsubscription_message(channels)
        return self.send_request(messages)
