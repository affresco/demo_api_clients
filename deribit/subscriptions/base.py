import abc
import time
import sched
import random
import string
import websocket
import threading

try:
    import ujson as json
except ImportError:
    import json


from .monitor import WebsocketMonitor
from utilities.id import  generate_id

# ##################################################################
# BASE CLASS
# ##################################################################

class DeltaWebsocketClient(abc.ABC):

    def __init__(self, callback, key=None, secret=None):

        # Socket itself
        self.__id = generate_id(6)
        self.__ws = None
        self.__url = "wss://www.delta.com/ws/api/v2"

        # Descriptive
        self.__callback = callback

        # Monitoring
        self.__monitor = WebsocketMonitor()
        self.__scheduler = sched.scheduler(time.time, time.sleep)

        # Credentials
        self.__key = key
        self.__secret = secret

        # Keeping track
        self.__pending_request = {}
        self.__acknowledged_request = {}

        # Open socket on startup
        self.run()

    # ####################################################################
    # SOCKET
    # ####################################################################

    @property
    def id(self):
        return self.__id

    @property
    def _ws(self):
        if not self.__ws:
            self.__ws = websocket.WebSocketApp(self.__url,
                                               on_message=lambda ws, msg: self.on_message(ws, msg),
                                               on_error=lambda ws, msg: self.on_error(ws, msg),
                                               on_close=lambda ws: self.on_close(ws),
                                               on_open=lambda ws: self.on_open(ws))
        return self.__ws

    def on_message(self, ws, message):
        msg = json.loads(message)
        return self.monitored_callback(msg)

    def on_error(self, ws, message):
        print(json.loads(message))

    def on_open(self, ws):

        print("Opening connection to delta.")

        # Authenticate the connection
        if self.__key and self.__secret:
            print("Authenticating connection.")
            msg = self._authentication()
            self.send_message(msg)

        # Wedge the websocket open
        wedge = self._keep_open()
        self.send_message(wedge)

    def on_close(self, ws):
        print("Closing connection to delta.")

    def send_message(self, message):
        return self._ws.send(json.dumps(message))

    # ####################################################################
    # SOCKET MANAGEMENT
    # ####################################################################

    def run(self, *args, **kwargs):
        th = threading.Thread(target=self.__safe_run,
                              args=args,
                              kwargs=kwargs,
                              daemon=True)
        th.start()
        time.sleep(0.25)

    def run_forever(self, *args, **kwargs):

        # Run the client
        self.run(*args, **kwargs)

        # Wait forever
        while True:
            time.sleep(0.00001)

    def __safe_run(self, *args, **kwargs):
        try:
            self._ws.run_forever(*args, **kwargs)
        except KeyboardInterrupt:
            print("Interrupted by user. Closing socket.")
        except ValueError:
            raise NotImplemented()
            # self.__safe_run(*args, **kwargs)

    def restart(self, callback=None, retry=0, *args, **kwargs):
        try:
            self.close()
            self.run()

            if callback:
                callback(*args, **kwargs)

        except:
            time.sleep(min(60, 2**retry))
            self.restart(callback, retry+1, *args, **kwargs)

    def close(self):
        try:
            self.__ws.safe_close()
        except:
            pass
        finally:
            self.__ws = None

    def add_to_pending(self, id, message):
        self.__pending_request[id] = message

    # ####################################################################
    # CALLBACK MONITORING & VALIDATION
    # ####################################################################

    @property
    def scheduler(self):
        return self.__scheduler

    def monitored_callback(self, message, *args, **kwargs):

        # Intercept acknowledgement messages
        if "id" in message:
            return self.acknowledge(message)

        # Monitoring
        message = self.__monitor.received(message)

        try:
            return self.__callback(message, *args, **kwargs)

        except FileNotFoundError:
            self.__monitor.failed(message)

    def acknowledge(self, message):

        # Extract id
        id = message["id"]

        # Message was expected
        if id in self.__pending_request:
            self.__acknowledged_request[id] = self.__pending_request[id]
            del self.__pending_request[id]
            print(f"[{id}] Request acknowledged.")

    def _purge(self):
        print("Purging pending queries.")
        if len(self.__pending_request) > 0:
            print("Warning: all queries were not acknowledged.")

    # ####################################################################
    # SUPPORT METHODS
    # ####################################################################

    @staticmethod
    def make_id_token():
        return ''.join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(7))

    @classmethod
    def _keep_open(cls):
        return {"jsonrpc": "2.0", "id": cls.make_id_token(), "method": "public/subscribe",
                "params": {"channels": ["book.PLACE_HOLDER"]}}

    def _authentication(self):
        return {"jsonrpc": "2.0", "id": self.make_id_token(), "method": "public/auth",
                "params": {"grant_type": "client_credentials",
                           "client_id": f"{self.__key}", "client_secret": f"{self.__secret}"}}

