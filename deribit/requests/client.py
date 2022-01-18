# Frameworks
import logging
import threading
import time

import websocket
from websocket._exceptions import WebSocketConnectionClosedException

import utilities.json as json_util

# Message builders
from deribit.messages import (mkt_data, session, account, trading)

# Import networking constants
# ####################################################################
# LOGGING
# ####################################################################

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ####################################################################
# LOGGING
# ####################################################################

MAX_STARTUP_TIME = 2.0
REQUEST_MAX_RETRIES = 10
CHECK_INTERVAL = 0.00001
STARTUP_SCALING = 10
REQUEST_TIMEOUT = 5.0


# ####################################################################
# DELTA CLIENT FOR PUNCTUAL REQUEST VIA HTTP GET
# ####################################################################

class DeltaSyncRequestClient(object):

    # ##################################################################
    # INIT
    # ##################################################################

    def __init__(self, url, key, secret):

        # Base uri
        self.__url = url
        self.__key = key
        self.__secret = secret

        # Time to establish the initial connection
        self.__startup_delay = 10  # in milliseconds

        # Properties
        self.__is_closing = False

        # Messages: information about SENT messages
        self.__sent_messages = {}
        self.__sent_messages_callbacks = {}

        # Messages: information about RECEIVED messages
        self.__answers_received = {}

        # Startup precautions
        self.__secured_connection = False

        # Last unexpected disconnect
        self.__disconnect_back_off = 0.25

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
        self.__is_closing = True

    # ##################################################################
    # EVENT HANDLERS
    # ##################################################################

    def _on_message(self, ws, message):

        # Parse the message to python data
        answer = json_util.loads(message)

        # Detect heartbeat request to keep socket alive
        params = answer.get("params")
        if params:
            type_ = params.get("type")

            # Exchange sending us a heartbeat
            if type_ == "heartbeat":
                return

            # Exchange asking us for a reply
            # to their heartbeat
            if type_ == "test_request":
                hb_resp_msg = session.test_heartbeat_request_message()
                self.ws.send(json_util.dumps(hb_resp_msg))
                return

        # Extract id_
        id_ = answer["id"]

        # Add to acknowledged messages
        self.__answers_received[id_] = answer

        # Invoke the callback if there is one, else do nothing
        # this assumes that if there is no callback, the method
        # generating the request is waiting for the reply
        if id_ in self.__sent_messages_callbacks:
            # Grab the callback
            cb = self.__sent_messages_callbacks[id_]

            # Clean up
            del self.__sent_messages[id_]
            del self.__sent_messages_callbacks[id_]
            del self.__answers_received[id_]

            return cb(answer)

    def _on_error(self, ws, message):
        logger.error(message)

    def _on_open(self, ws):

        logger.info("Opening web socket connection.")

        credentials = session.login_message(key=self.__key, secret=self.__secret)
        id_ = credentials["id"]

        self.__sent_messages[id_] = credentials
        self.__sent_messages_callbacks[id_] = self._on_login

        ws.send(json_util.dumps(credentials))

    def _on_login(self, message):

        if not "error" in message:
            self.__secured_connection = True
            print("Web socket opened.")

            self.__disconnect_back_off = 0.25

            # Enable heartbeat
            enable_heartbeat_msg = session.set_heartbeat_message()
            self.ws.send(json_util.dumps(enable_heartbeat_msg))


        else:
            pass

    def _on_close(self, ws):
        print("Socket closed.")

        # Was supposed to happen
        if self.__is_closing:
            try:
                ws.retire()
            except:
                pass
        # Not expected
        else:
            logger.warning("Connection ended unexpectedly. Reconnecting to web socket server.")
            self.__ws = None

            # Back off:
            self.__disconnect_back_off *= 2
            time.sleep(min(10.0, self.__disconnect_back_off))

            self.maybe_reconnect()

    def _on_ping(self, ws, message, *args, **kwargs):
        print(f"On Ping: {message}")

    def _on_pong(self, ws, message, *args, **kwargs):
        print(f"On Pong: {message}")

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
            self.run_forever_on_thread(ws, startup_delay=self.__startup_delay)

    # ##################################################################
    # WEBSOCKET BASIC OPERATIONS
    # ##################################################################

    @property
    def ws(self):
        if not self.__ws:
            self.maybe_reconnect()
        return self.__ws

    def request(self, message, callback=None):
        msg_cb = [(message, callback)]
        return self.__requests(msg_cb)

    def __requests(self, messages_with_callbacks, retry=0):

        try:

            if retry > REQUEST_MAX_RETRIES:
                raise ConnectionAbortedError("Maximum number of retries reached.")

            # Look for broken connections
            self.maybe_reconnect()

            gentle_delay = 0.05 if len(messages_with_callbacks) > 50 else 0.0

            counter = 0
            while not self.__secured_connection and counter < MAX_STARTUP_TIME:
                time.sleep(CHECK_INTERVAL)
                counter += CHECK_INTERVAL

            # Send each message
            waiting_ids = []
            for msg_tuple in messages_with_callbacks:

                msg, cb = msg_tuple[0], msg_tuple[1]

                id_ = msg["id"]
                self.ws.send(json_util.dumps(msg))
                self.__sent_messages[id_] = msg

                if cb:
                    self.__sent_messages_callbacks[id_] = cb
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
            return self.__requests(messages_with_callbacks=messages_with_callbacks,
                                   retry=retry)

    def __wait_blocking(self, ids):

        ids = ids if isinstance(ids, list) else [ids]
        total_number_of_ids = len(ids)

        waiting_time = 0.0
        result, queue = {}, self.__answers_received

        while waiting_time < REQUEST_TIMEOUT:

            # If the number of answers is not even the length of our
            # messages, leave it be...
            if len(self.__answers_received) >= total_number_of_ids:

                result = {id: queue[id] for id in ids if id in queue}

                if len(result) == total_number_of_ids:
                    break

            # Some answers are missing, wait a bit...
            time.sleep(CHECK_INTERVAL)
            waiting_time += CHECK_INTERVAL

        # Clean up
        for id in ids:
            try:
                del self.__answers_received[id]
                del self.__sent_messages[id]
            except:
                pass

        # Return
        return list(result.values())

    # ##################################################################
    # SESSION
    # ##################################################################

    # ##############################
    # SERVER TIME
    # ##############################

    def server_time(self, callback=None):

        # Produce message to be sent externally
        msg = session.get_time()

        # Make request
        return self.request(msg, callback)

    # ##############################
    # TEST
    # ##############################

    def test(self, callback=None):
        msg = session.test_no_exception()
        return self.request(msg, callback)

    def test_exception(self, callback=None):
        # Careful this closed the socket from Delta's end
        msg = session.test_with_exception()
        return self.request(msg, callback)

    # ##################################################################
    # MARKET DATA
    # ##################################################################

    # ##############################
    # INDEX LEVEL
    # ##############################

    def index_level(self, currency: str, callback=None):
        msg = mkt_data.request_index(currency=currency)
        return self.request(msg, callback)

    def btc_index(self, callback=None):
        return self.index_level(currency="BTC", callback=callback)

    def eth_index(self, callback=None):
        return self.index_level(currency="ETH", callback=callback)

    # ##############################
    # INSTRUMENTS
    # ##############################

    def instruments(self, currency=None, kind=None, expired=None, callback=None):
        msg = mkt_data.request_instruments(currency=currency, kind=kind, expired=expired)
        msg_cb = [(m, callback) for m in msg]
        return self.__requests(msg_cb)

    # ##############################
    # CURRENCIES
    # ##############################

    def currencies(self, callback=None):
        msg = mkt_data.request_currencies()
        return self.request(msg, callback)

    # ##############################
    # ORDERBOOKS (SNAPSHOT)
    # ##############################

    def orderbooks(self, instruments, depth, callback=None):

        if not isinstance(instruments, list):
            instruments = [instruments]

        msg = mkt_data.request_orderbooks(instruments=instruments, depth=depth)
        msg_cb = [(m, callback) for m in msg]
        return self.__requests(msg_cb)

    # ##############################
    # QUOTES
    # ##############################

    def quotes(self, instruments, callback=None):
        msg = mkt_data.request_quotes(instruments)
        msg_cb = [(m, callback) for m in msg]
        return self.__requests(msg_cb)

    # ##############################
    # SUMMARY
    # ##############################

    def book_summary_by_currency(self, currency, callback=None):
        msg = mkt_data.request_book_summary_by_currency(currency)
        return self.request(msg, callback)

    def book_summary_by_instrument(self, instrument, callback=None):
        msg = mkt_data.request_book_summary_by_instrument(instrument)
        return self.request(msg, callback)

    # ##############################
    # TRADES -- LEGACY
    # ##############################
    """
    def last_trades_by_instrument(self, instrument: str,
                                  count: int = None,
                                  include_old: bool = True,
                                  start_seq: int = None,
                                  end_seq: int = None,
                                  callback=None):

        msg = mkt_data.request_last_trades_by_instrument(instrument=instrument,
                                                         count=count,
                                                         include_old=include_old,
                                                         start_seq=start_seq,
                                                         end_seq=end_seq)

        return self.request(msg, callback)

    """

    # ##############################
    # TRADES -- NEW VERSION
    # ##############################

    def trades(self, instruments,
               count: int = None,
               include_old: bool = True,
               start_seq: int = None,
               end_seq: int = None,
               callback=None):

        msg = mkt_data.request_trades(instruments=instruments,
                                      count=count,
                                      include_old=include_old,
                                      start_seq=start_seq,
                                      end_seq=end_seq)

        msg_cb = [(m, callback) for m in msg]
        return self.__requests(msg_cb)

    def all_trades(self, instruments, callback=None):

        latest_trades = self.trades(instruments=instruments, count=1, include_old=True)
        messages = mkt_data.request_all_trades(latest_trades)

        msg_cb = [(m, callback) for m in messages]
        return self.__requests(msg_cb)

    # ##################################################################
    # ACCOUNT
    # ##################################################################

    # ##############################
    # POSITION (ON ONE INSTRUMENT)
    # ##############################

    def position(self, instrument: str, callback=None):
        msg = account.get_position(instrument=instrument)
        return self.request(msg, callback)

    # ##############################
    # ALL POSITIONS
    # ##############################

    def all_positions(self, currency=None, kind=None, callback=None):

        msg = account.get_all_positions(currency=currency,
                                        kind=kind)
        msg = [(m, callback) for m in msg]
        return self.__requests(msg)

    # ##############################
    # ACCOUNT SUMMARY
    # ##############################

    def account_summary(self, currency, extended=True, callback=None):
        msg = account.get_account_summary(currency=currency,
                                          extended=extended)
        return self.request(msg, callback)

    # ##############################
    # ANNOUNCEMENTS
    # ##############################

    def announcements(self, callback=None):
        msg = account.get_announcements()
        return self.request(msg, callback)

    # ##############################
    # API KEYS
    # ##############################

    def create_api_key(self, name: str, account_: int, trading: int, default: bool = False, callback=None):

        # Produce message to be sent externally
        msg = account.create_api_key(account=str(account_), trade=str(trading), name=name, default=default)

        # Make request
        return self.request(msg, callback)

    def delete_api_key(self, id, callback=None):

        # Produce message to be sent externally
        msg = account.remove_api_key(id)

        # Make request
        return self.request(msg, callback)

    # ##############################
    # SUB-ACCOUNTS
    # ##############################

    def list_sub_accounts(self, with_portfolio=False, callback=None):

        # Produce message to be sent externally
        msg = account.get_sub_accounts(with_portfolio=with_portfolio)

        # Make request
        return self.request(msg, callback)

    def create_sub_account(self, callback=None):

        # Produce message to be sent externally
        msg = account.get_create_sub_account()

        # Make request
        return self.request(msg, callback)

    def change_name_of_sub_account(self, sid, name, callback=None):

        # Produce message to be sent externally
        msg = account.change_name_of_sub_account(id_=sid, name=name)

        # Make request
        return self.request(msg, callback)

    # ##################################################################
    # TRADING
    # ##################################################################

    # ##############################
    # BUY
    # ##############################

    def buy(self,
            instrument: str,
            amount: float,
            order_type: str = None,
            label: str = None,
            limit_price: float = None,
            time_in_force: str = None,
            max_show: float = None,
            post_only: bool = False,
            reduce_only: bool = False,
            stop_price: float = None,
            trigger: str = None,
            vol_quote: bool = False,
            callback=None):

        msg = trading.buy(instrument=instrument,
                          amount=amount,
                          order_type=order_type,
                          label=label,
                          limit_price=limit_price,
                          time_in_force=time_in_force,
                          max_show=max_show,
                          post_only=post_only,
                          reduce_only=reduce_only,
                          stop_price=stop_price,
                          trigger=trigger,
                          vol_quote=vol_quote)

        return self.request(msg, callback)

    # ##############################
    # SELL
    # ##############################

    def sell(self,
             instrument: str,
             amount: float,
             order_type: str = None,
             label: str = None,
             limit_price: float = None,
             time_in_force: str = None,
             max_show: float = None,
             post_only: bool = False,
             reduce_only: bool = False,
             stop_price: float = None,
             trigger: str = None,
             vol_quote: bool = False,
             callback=None):

        msg = trading.sell(instrument=instrument,
                           amount=amount,
                           order_type=order_type,
                           label=label,
                           limit_price=limit_price,
                           time_in_force=time_in_force,
                           max_show=max_show,
                           post_only=post_only,
                           reduce_only=reduce_only,
                           stop_price=stop_price,
                           trigger=trigger,
                           vol_quote=vol_quote)

        return self.request(msg, callback)

    # ##############################
    # CLOSE
    # ##############################

    def close(self,
              instrument: str,
              order_type: str = None,
              limit_price: float = None,
              callback=None):

        msg = trading.close(instrument=instrument,
                            order_type=order_type,
                            limit_price=limit_price)

        return self.request(msg, callback)

    # ##############################
    # CANCEL ALL OPEN ORDERS
    # ##############################

    def cancel_all(self, callback=None):
        msg = trading.cancel_all()
        return self.request(msg, callback)

    # ##############################
    # CANCEL ALL (GIVEN CURRENCY)
    # ##############################

    def cancel_all_by_currency(self, currency: str, kind: str = None, order_type: str = None, callback=None):
        msg = trading.cancel_all_by_currency(currency=currency,
                                             kind=kind,
                                             order_type=order_type)
        return self.request(msg, callback)

    # ##############################
    # CANCEL ALL (GIVEN INSTRUMENT)
    # ##############################

    def cancel_all_by_instrument(self, instrument: str, order_type: str = None, callback=None):
        msg = trading.cancel_all_by_instrument(instrument=instrument,
                                               order_type=order_type)
        return self.request(msg, callback)

    # ##############################
    # MARGIN ESTIMATE
    # ##############################

    def estimate_margins(self, instrument: str, amount: float, price: float, callback=None):
        msg = trading.margins(instrument=instrument,
                              amount=amount,
                              price=price)
        return self.request(msg, callback)

    # ##############################
    # OPEN ORDERS (GIVEN CURRENCY)
    # ##############################

    def open_orders_by_currency(self, currency: str, kind: str = None,
                                order_type: float = None, callback=None):
        msg = trading.open_orders_by_currency(currency=currency,
                                              kind=kind,
                                              order_type=order_type)
        return self.request(msg, callback)

    # ##############################
    # OPEN ORDERS (GIVEN INSTRUMENT)
    # ##############################

    def open_orders_by_instrument(self, instrument: str, order_type: float = None, callback=None):
        msg = trading.open_orders_by_instrument(instrument=instrument,
                                                order_type=order_type)
        return self.request(msg, callback)

    # ##############################
    # USER TRADES (GIVEN CURRENCY)
    # ##############################

    def user_trades_by_currency(self, currency: str, kind: str = None,
                                count: int = None,
                                include_old: bool = False,
                                callback=None):
        msg = trading.user_trades_by_currency(currency=currency,
                                              kind=kind,
                                              count=count,
                                              include_old=include_old)
        return self.request(msg, callback)

    # ##############################
    # USER TRADES (GIVEN INSTRUMENT)
    # ##############################

    def user_trades_by_instrument(self, instrument: str, count: int = None, include_old: bool = None, callback=None):
        msg = trading.user_trades_by_instrument(instrument=instrument,
                                                count=count,
                                                include_old=include_old)
        return self.request(msg, callback)

    # ##############################
    # ORDER STATUS
    # ##############################

    def order_status(self, order_id: str, callback=None):
        msg = trading.order_status(order_id=order_id)
        return self.request(msg, callback)
