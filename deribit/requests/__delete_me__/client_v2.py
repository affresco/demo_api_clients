import sys
import json
import logging
import websockets
from blinker import signal

# Sync wrapper
from deribit.requests.utilties import sync_wrapper

# Message builders
from deribit.messages import (mkt_data, session, account, trading)

# Import some delta specific classes
from deribit.support.settings import (DEFAULT_CURRENCY, DEFAULT_DEPTH)

from deribit.requests.__delete_me__.base_v2 import DeltaSyncBaseClient

# ####################################################################
# LOGGING
# ####################################################################

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ####################################################################
# KEY EVENT FOR LOG IN
# ####################################################################

login = signal("DELTA-CLIENT-LOGIN")


# ####################################################################
# CALLBACK
# ####################################################################

def _default_callback(data):
    return data


# ####################################################################
# DELTA CLIENT FOR PUNCTUAL REQUEST VIA HTTP GET
# ####################################################################


class DeltaSyncRequestClient(DeltaSyncBaseClient):

    def __init__(self, url, key, secret, **kwargs):

        # Base uri
        self.__url = url
        super(DeltaSyncRequestClient, self).__init__(key=key, secret=secret)

        # Login signal handle
        def handle_signal_login(sender, data=None, websocket=None, **kwargs):
            self.on_delta_login(sender, data, websocket, **kwargs)

        # Set kwargs
        for k in kwargs:
            self.__setattr__(name=k, value=kwargs[k])

        self.handle_signal_login = handle_signal_login
        login.maybe_reconnect(handle_signal_login)

        # ##################################################################
        # WEBSOCKET BASIC OPERATIONS
        # ##################################################################

    @staticmethod
    def on_message(data, **kwargs):
        return data

    async def __async_request(self, messages, auth_required=False, handle=None):

        # Providing handle if required
        # has_handle = True
        if not handle:
            handle, has_handle = self.on_message, False

        if not isinstance(messages, list):
            messages = [messages]

        async with websockets.connect(self.__url, max_size=sys.maxsize) as websocket:

            logger.info("Client connecting.")

            if auth_required or not self.is_logged_in:
                logger.info("Logging required.")

                # Authenticate the connection
                log_msg = self.login_message()
                await websocket.send(json.dumps(log_msg))
                login_response = await websocket.recv()

                # Store token if first login
                if not self.is_logged_in:
                    logger.info(f"[{self.id}] Logging in client.")
                    login.send(data=json.loads(login_response))
                    self.__is_logged_in = True
                    logger.info(f"[{self.id}] Logging successful.")

            # Authenticate the messages to be sent
            # if auth_required:
            #    messages = [self.auth_with_access_token(messages=msg) for msg in messages]

            _json_msg = [json.dumps(m) for m in messages]
            response = []

            # Gather async celery_tasks and return
            for m in _json_msg:
                await websocket.send(m)
                r = await websocket.recv()
                response.append(json.loads(r))

            return handle(data=response)

    # ##################################################################
    # SESSION
    # ##################################################################

    # ##############################
    # SERVER TIME
    # ##############################

    async def async_server_time(self, handle=None):
        msg = session.get_time()

        return await self.__async_request(messages=msg, auth_required=False, handle=handle)

    def server_time(self, handle=None):
        delegate = self.async_server_time
        return sync_wrapper(delegate, handle=handle)

    # ##############################
    # TEST (WORKING OK)
    # ##############################

    async def async_test(self, handle=None):
        msg = session.test_no_exception()

        return await self.__async_request(messages=msg, auth_required=False, handle=handle)

    def test(self, handle=None):
        delegate = self.async_test
        return sync_wrapper(delegate, handle=handle)

    # ##############################
    # TEST (delta THROW EXCEPTION)
    # ##############################

    async def async_test_exception(self, handle=None):
        msg = session.test_with_exception()

        return await self.__async_request(messages=msg, auth_required=False, handle=handle)

    def test_exception(self, handle=None):
        delegate = self.async_test_exception
        return sync_wrapper(delegate, handle=handle)

    # ##################################################################
    # MARKET DATA
    # ##################################################################

    # ##############################
    # INDEX LEVEL
    # ##############################

    async def async_index_level(self, currency: str, handle=None):
        msg = mkt_data.request_index(currency=currency)

        return await self.__async_request(messages=msg, auth_required=False, handle=handle)

    def index_level(self, currency: str, handle=None):
        delegate = self.async_index_level
        return sync_wrapper(delegate, currency=currency, handle=handle)

    def btc_index(self, handle=None):
        return self.index_level(currency="BTC", handle=handle)

    def eth_index(self, handle=None):
        return self.index_level(currency="ETH", handle=handle)

    # ##############################
    # INSTRUMENTS
    # ##############################

    async def async_instruments(self, currency=None, kind=None, expired=None, handle=None):

        msg = mkt_data.request_instruments(currency=currency, kind=kind, expired=expired)

        return await self.__async_request(messages=msg,
                                          auth_required=False,
                                          handle=handle)

    def instruments(self, currency=None, kind=None, expired=None, handle=None):
        delegate = self.async_instruments
        return sync_wrapper(delegate, currency=currency, kind=kind, expired=expired, handle=handle)

    # ##############################
    # CURRENCIES
    # ##############################

    async def async_currencies(self, handle=None):

        msg = mkt_data.request_currencies()

        return await self.__async_request(messages=msg,
                                          auth_required=False,
                                          handle=handle)

    def currencies(self, handle=None):
        delegate = self.async_currencies
        return sync_wrapper(delegate, handle=handle)

    # ##############################
    # ORDERBOOKS (SNAPSHOT)
    # ##############################

    async def async_orderbooks(self, instruments, depth=DEFAULT_DEPTH, handle=None):

        if not isinstance(instruments, list):
            instruments = [instruments]

        msg = mkt_data.request_orderbooks(instruments=instruments, depth=depth)

        return await self.__async_request(messages=msg,
                                          auth_required=False,
                                          handle=handle)

    def orderbooks(self, instruments, depth=DEFAULT_DEPTH, handle=None):
        delegate = self.async_orderbooks
        return sync_wrapper(delegate, instruments=instruments, depth=depth, handle=handle)

    # ##############################
    # QUOTES
    # ##############################

    async def async_quotes(self, instruments, handle=None):

        msg = mkt_data.request_quotes(instruments)

        return await self.__async_request(messages=msg,
                                          auth_required=False,
                                          handle=handle)

    def quotes(self, instruments, handle=None):
        delegate = self.async_quotes
        return sync_wrapper(delegate, instruments=instruments, handle=handle)

    # ##############################
    # SUMMARY
    # ##############################

    async def async_book_summary_by_currency(self, currency, handle=None):

        msg = mkt_data.request_book_summary_by_currency(currency)

        return await self.__async_request(messages=msg,
                                          auth_required=False,
                                          handle=handle)

    def book_summary_by_currency(self, currency, handle=None):
        delegate = self.async_book_summary_by_currency
        return sync_wrapper(delegate, currency=currency, handle=handle)

    async def async_book_summary_by_instrument(self, instrument, handle=None):

        msg = mkt_data.request_book_summary_by_instrument(instrument)

        return await self.__async_request(messages=msg,
                                          auth_required=False,
                                          handle=handle)

    def book_summary_by_instrument(self, instrument, handle=None):
        delegate = self.async_book_summary_by_instrument
        return sync_wrapper(delegate, instrument=instrument, handle=handle)

    # ##############################
    # TRADES -- LEGACY
    # ##############################

    async def async_last_trades_by_instrument(self, instrument: str,
                                              count: int = None,
                                              include_old: bool = True,
                                              start_seq: int = None,
                                              end_seq: int = None, handle=None):

        msg = mkt_data.request_last_trades_by_instrument(instrument=instrument,
                                                         count=count,
                                                         include_old=include_old,
                                                         start_seq=start_seq,
                                                         end_seq=end_seq)

        return await self.__async_request(messages=msg,
                                          auth_required=False,
                                          handle=handle)

    def last_trades_by_instrument(self, instrument: str,
                                  count: int = None,
                                  include_old: bool = True,
                                  start_seq: int = None,
                                  end_seq: int = None,
                                  handle=None):

        delegate = self.async_last_trades_by_instrument
        return sync_wrapper(delegate,
                            instrument=instrument,
                            count=count,
                            include_old=include_old,
                            start_seq=start_seq,
                            end_seq=end_seq,
                            handle=handle)

    # ##############################
    # TRADES -- NEW VERSION
    # ##############################

    async def async_trades(self, instruments,
                           count: int = None,
                           include_old: bool = True,
                           start_seq: int = None,
                           end_seq: int = None, handle=None):

        msg = mkt_data.request_trades(instruments=instruments,
                                      count=count,
                                      include_old=include_old,
                                      start_seq=start_seq,
                                      end_seq=end_seq)

        return await self.__async_request(messages=msg,
                                          auth_required=False,
                                          handle=handle)

    def trades(self, instruments,
               count: int = None,
               include_old: bool = True,
               start_seq: int = None,
               end_seq: int = None,
               handle=None):

        delegate = self.async_trades
        return sync_wrapper(delegate,
                            instruments=instruments,
                            count=count,
                            include_old=include_old,
                            start_seq=start_seq,
                            end_seq=end_seq,
                            handle=handle)

    async def __async_all_trades(self, messages, handle=None):
        return await self.__async_request(messages=messages,
                                          auth_required=False,
                                          handle=handle)

    def all_trades(self, instruments, handle=None):

        def loopback(data):
            return mkt_data.request_all_trades(data=data)

        messages = sync_wrapper(self.async_trades,
                                instruments=instruments,
                                count=1,
                                include_old=True,
                                handle=loopback)

        return sync_wrapper(self.__async_all_trades,
                            messages=messages,
                            handle=handle)

    # ##################################################################
    # ACCOUNT
    # ##################################################################

    # ##############################
    # POSITION (ON ONE INSTRUMENT)
    # ##############################

    async def async_position(self, instrument: str, handle=None):
        msg = account.get_position(instrument=instrument)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          handle=handle)

    def position(self, instruments: str, handle=None):
        delegate = self.async_position
        return sync_wrapper(delegate, instruments=instruments, handle=handle)

    # ##############################
    # ALL POSITIONS
    # ##############################

    async def async_all_positions(self, currency=None, kind=None, handle=None):

        msg = account.get_all_positions(currency=currency,
                                        kind=kind)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          handle=handle)

    def all_positions(self, currency=None, kind=None, handle=None):
        delegate = self.async_all_positions
        return sync_wrapper(delegate, currency=currency, kind=kind, handle=handle)

    # ##############################
    # ACCOUNT SUMMARY
    # ##############################

    async def async_account_summary(self, currency=DEFAULT_CURRENCY, extended=True, handle=None):

        msg = account.get_account_summary(currency=currency,
                                          extended=extended)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          handle=handle)

    def account_summary(self, currency=DEFAULT_CURRENCY, extended=True, handle=None):
        delegate = self.async_account_summary
        return sync_wrapper(delegate, currency=currency, extended=extended, handle=handle)

    # ##############################
    # ANNOUNCEMENTS
    # ##############################

    async def async_announcements(self, handle=None):

        msg = account.get_announcements()

        return await self.__async_request(messages=msg,
                                          auth_required=False,
                                          handle=handle)

    def announcements(self, handle=None):
        delegate = self.async_announcements
        return sync_wrapper(delegate, handle=handle)

    # ##################################################################
    # TRADING
    # ##################################################################

    # ##############################
    # BUY
    # ##############################

    async def async_buy(self,
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
                        handle=None):

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

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          handle=handle)

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
            handle=None):

        delegate = self.async_buy
        return sync_wrapper(delegate,
                            instrument=instrument,
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
                            vol_quote=vol_quote,
                            handle=handle)

    # ##############################
    # SELL
    # ##############################

    async def async_sell(self,
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
                         handle=None):

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

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          # handle=trade_sell_received.send,
                                          handle=handle)

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
             handle=None):

        delegate = self.async_sell
        return sync_wrapper(delegate,
                            instrument=instrument,
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
                            vol_quote=vol_quote,
                            handle=handle)

    # ##############################
    # CLOSE
    # ##############################

    async def async_close(self,
                          instrument: str,
                          order_type: str = None,
                          limit_price: float = None,
                          handle=None):

        msg = trading.close(instrument=instrument,
                            order_type=order_type,
                            limit_price=limit_price)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          # handle=trade_close_received.send,
                                          handle=handle)

    def close(self,
              instrument: str,
              order_type: str = None,
              limit_price: float = None,
              handle=None):

        delegate = self.async_close
        return sync_wrapper(delegate,
                            instrument=instrument,
                            order_type=order_type,
                            limit_price=limit_price,
                            handle=handle)

    # ##############################
    # CANCEL ALL OPEN ORDERS
    # ##############################

    async def async_cancel_all(self, handle=None):
        msg = trading.cancel_all()

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          # handle=trade_cancel_all_received,
                                          handle=handle)

    def cancel_all(self, handle=None):
        delegate = self.async_cancel_all
        return sync_wrapper(delegate, handle=handle)

    # ##############################
    # CANCEL ALL (GIVEN CURRENCY)
    # ##############################

    async def async_cancel_all_by_currency(self, currency: str, kind: str = None, order_type: str = None, handle=None):

        msg = trading.cancel_all_by_currency(currency=currency,
                                             kind=kind,
                                             order_type=order_type)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          # handle=trade_cancel_received.send,
                                          handle=handle)

    def cancel_all_by_currency(self, currency: str, kind: str = None, order_type: str = None, handle=None):
        delegate = self.async_cancel_all_by_currency
        return sync_wrapper(delegate, currency=currency, kind=kind, order_type=order_type, handle=handle)

    # ##############################
    # CANCEL ALL (GIVEN INSTRUMENT)
    # ##############################

    async def async_cancel_all_by_instrument(self, instrument: str, order_type: str = None, handle=None):

        msg = trading.cancel_all_by_instrument(instrument=instrument,
                                               order_type=order_type)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          # handle=trade_cancel_received.send,
                                          handle=handle)

    def cancel_all_by_instrument(self, instrument: str, order_type: str = None, handle=None):
        delegate = self.async_cancel_all_by_instrument
        return sync_wrapper(delegate, instrument=instrument, order_type=order_type, handle=handle)

    # ##############################
    # MARGIN ESTIMATE
    # ##############################

    async def async_estimate_margins(self, instrument: str, amount: float, price: float, handle=None):

        msg = trading.margins(instrument=instrument,
                              amount=amount,
                              price=price)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          # handle=trade_margin_estimate_received.send,
                                          handle=handle)

    def estimate_margins(self, instrument: str, amount: float, price: float, handle=None):
        delegate = self.async_estimate_margins
        return sync_wrapper(delegate,
                            instrument=instrument,
                            amount=amount,
                            price=price,
                            handle=handle)

    # ##############################
    # OPEN ORDERS (GIVEN CURRENCY)
    # ##############################

    async def async_open_orders_by_currency(self, currency: str, kind: str = None,
                                            order_type: float = None, handle=None):

        msg = trading.open_orders_by_currency(currency=currency,
                                              kind=kind,
                                              order_type=order_type)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          # handle=trade_open_orders_received.send,
                                          handle=handle)

    def open_orders_by_currency(self, currency: str, kind: str = None,
                                order_type: float = None, handle=None):
        delegate = self.async_open_orders_by_currency
        return sync_wrapper(delegate,
                            currency=currency,
                            kind=kind,
                            order_type=order_type,
                            handle=handle)

    # ##############################
    # OPEN ORDERS (GIVEN INSTRUMENT)
    # ##############################

    async def async_open_orders_by_instrument(self, instrument: str, order_type: float = None, handle=None):

        msg = trading.open_orders_by_instrument(instrument=instrument,
                                                order_type=order_type)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          # handle=trade_open_orders_received.send,
                                          handle=handle)

    def open_orders_by_instrument(self, instrument: str, order_type: float = None, handle=None):
        delegate = self.async_open_orders_by_instrument
        return sync_wrapper(delegate,
                            instrument=instrument,
                            order_type=order_type,
                            handle=handle)

    # ##############################
    # USER TRADES (GIVEN CURRENCY)
    # ##############################

    async def async_user_trades_by_currency(self, currency: str, kind: str = None,
                                            count: int = None,
                                            include_old: bool = False, handle=None):

        msg = trading.user_trades_by_currency(currency=currency,
                                              kind=kind,
                                              count=count,
                                              include_old=include_old)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          # handle=trade_history_received.send,
                                          handle=handle)

    def user_trades_by_currency(self, currency: str, kind: str = None,
                                count: int = None,
                                include_old: bool = False,
                                handle=None):
        delegate = self.async_user_trades_by_currency
        return sync_wrapper(delegate,
                            currency=currency,
                            kind=kind,
                            count=count,
                            include_old=include_old,
                            handle=handle)

    # ##############################
    # USER TRADES (GIVEN INSTRUMENT)
    # ##############################

    async def async_user_trades_by_instrument(self, instrument: str, count: int = None, include_old: bool = None,
                                              handle=None):

        msg = trading.user_trades_by_instrument(instrument=instrument,
                                                count=count,
                                                include_old=include_old)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          # handle=trade_history_received.send,
                                          handle=handle)

    def user_trades_by_instrument(self, instrument: str, count: int = None, include_old: bool = None, handle=None):
        delegate = self.async_user_trades_by_instrument
        return sync_wrapper(delegate,
                            instrument=instrument,
                            count=count,
                            include_old=include_old,
                            handle=handle)

    # ##############################
    # ORDER STATUS
    # ##############################

    async def async_order_status(self, order_id: str, handle=None):

        msg = trading.order_status(order_id=order_id)

        return await self.__async_request(messages=msg,
                                          auth_required=True,
                                          # handle=trade_order_status_received.send,
                                          handle=handle)

    def order_status(self, order_id: str, handle=None):
        delegate = self.async_order_status
        return sync_wrapper(delegate, order_id=order_id, handle=handle)
