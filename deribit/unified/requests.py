from deribit.unified.base import UnifiedClient
from deribit.messages import (mkt_data,
                                        session,
                                        account,
                                        trading)


class RequestClient(UnifiedClient):

    def __init__(self, url, key, secret, name=None):
        super().__init__(url=url,
                         key=key,
                         secret=secret,
                         name=name,

                         # Default callback is used
                         # for subscriptions only
                         callback=None)

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
        return self.send_request(msg, callback)

    # ##############################
    # TEST
    # ##############################

    def test(self, callback=None):
        msg = session.test_no_exception()
        return self.send_request(msg, callback)

    def test_exception(self, callback=None):
        # Careful this closed the socket from Delta's end
        msg = session.test_with_exception()
        return self.send_request(msg, callback)

    # ##################################################################
    # MARKET DATA
    # ##################################################################

    # ##############################
    # INDEX LEVEL
    # ##############################

    def index_level(self, currency: str, callback=None):
        msg = mkt_data.request_index(currency=currency)
        return self.send_request(msg, callback)

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
        return self.send_multiple_requests(msg_cb)

    # ##############################
    # CURRENCIES
    # ##############################

    def currencies(self, callback=None):
        msg = mkt_data.request_currencies()
        return self.send_request(msg, callback)

    # ##############################
    # ORDERBOOKS (SNAPSHOT)
    # ##############################

    def orderbooks(self, instruments, depth, callback=None):
        if not isinstance(instruments, list):
            instruments = [instruments]

        msg = mkt_data.request_orderbooks(instruments=instruments, depth=depth)
        msg_cb = [(m, callback) for m in msg]
        return self.send_multiple_requests(msg_cb)

    # ##############################
    # QUOTES
    # ##############################

    def quotes(self, instruments, callback=None):
        msg = mkt_data.request_quotes(instruments)
        msg_cb = [(m, callback) for m in msg]
        return self.send_multiple_requests(msg_cb)

    # ##############################
    # SUMMARY
    # ##############################

    def book_summary_by_currency(self, currency, callback=None):
        msg = mkt_data.request_book_summary_by_currency(currency)
        return self.send_request(msg, callback)

    def book_summary_by_instrument(self, instrument, callback=None):
        msg = mkt_data.request_book_summary_by_instrument(instrument)
        return self.send_request(msg, callback)

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
        return self.send_multiple_requests(msg_cb)

    def all_trades(self, instruments, callback=None):
        latest_trades = self.trades(instruments=instruments, count=1, include_old=True)
        messages = mkt_data.request_all_trades(latest_trades)

        msg_cb = [(m, callback) for m in messages]
        return self.send_multiple_requests(msg_cb)

    # ##################################################################
    # ACCOUNT
    # ##################################################################

    # ##############################
    # POSITION (ON ONE INSTRUMENT)
    # ##############################

    def position(self, instrument: str, callback=None):
        msg = account.get_position(instrument=instrument)
        return self.send_request(msg, callback)

    # ##############################
    # ALL POSITIONS
    # ##############################

    def all_positions(self, currency=None, kind=None, callback=None):
        msg = account.get_all_positions(currency=currency,
                                        kind=kind)
        msg = [(m, callback) for m in msg]
        return self.send_multiple_requests(msg)

    # ##############################
    # ACCOUNT SUMMARY
    # ##############################

    def account_summary(self, currency, extended=True, callback=None):
        msg = account.get_account_summary(currency=currency,
                                          extended=extended)
        return self.send_request(msg, callback)

    # ##############################
    # ANNOUNCEMENTS
    # ##############################

    def announcements(self, callback=None):
        msg = account.get_announcements()
        return self.send_request(msg, callback)

    # ##############################
    # API KEYS
    # ##############################

    def create_api_key(self, name: str, account_: int, trading: int, default: bool = False, callback=None):
        # Produce message to be sent externally
        msg = account.create_api_key(account=str(account_), trade=str(trading), name=name, default=default)

        # Make request
        return self.send_request(msg, callback)

    def delete_api_key(self, id, callback=None):
        # Produce message to be sent externally
        msg = account.remove_api_key(id)

        # Make request
        return self.send_request(msg, callback)

    # ##############################
    # SUB-ACCOUNTS
    # ##############################

    def list_sub_accounts(self, with_portfolio=False, callback=None):
        # Produce message to be sent externally
        msg = account.get_sub_accounts(with_portfolio=with_portfolio)

        # Make request
        return self.send_request(msg, callback)

    def create_sub_account(self, callback=None):
        # Produce message to be sent externally
        msg = account.get_create_sub_account()

        # Make request
        return self.send_request(msg, callback)

    def change_name_of_sub_account(self, sid, name, callback=None):
        # Produce message to be sent externally
        msg = account.change_name_of_sub_account(id_=sid, name=name)

        # Make request
        return self.send_request(msg, callback)

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

        return self.send_request(msg, callback)

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

        return self.send_request(msg, callback)

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

        return self.send_request(msg, callback)

    # ##############################
    # CANCEL ALL OPEN ORDERS
    # ##############################

    def cancel_all(self, callback=None):
        msg = trading.cancel_all()
        return self.send_request(msg, callback)

    # ##############################
    # CANCEL ALL (GIVEN CURRENCY)
    # ##############################

    def cancel_all_by_currency(self, currency: str, kind: str = None, order_type: str = None, callback=None):
        msg = trading.cancel_all_by_currency(currency=currency,
                                             kind=kind,
                                             order_type=order_type)
        return self.send_request(msg, callback)

    # ##############################
    # CANCEL ALL (GIVEN INSTRUMENT)
    # ##############################

    def cancel_all_by_instrument(self, instrument: str, order_type: str = None, callback=None):
        msg = trading.cancel_all_by_instrument(instrument=instrument,
                                               order_type=order_type)
        return self.send_request(msg, callback)

    # ##############################
    # MARGIN ESTIMATE
    # ##############################

    def estimate_margins(self, instrument: str, amount: float, price: float, callback=None):
        msg = trading.margins(instrument=instrument,
                              amount=amount,
                              price=price)
        return self.send_request(msg, callback)

    # ##############################
    # OPEN ORDERS (GIVEN CURRENCY)
    # ##############################

    def open_orders_by_currency(self, currency: str, kind: str = None,
                                order_type: float = None, callback=None):
        msg = trading.open_orders_by_currency(currency=currency,
                                              kind=kind,
                                              order_type=order_type)
        return self.send_request(msg, callback)

    # ##############################
    # OPEN ORDERS (GIVEN INSTRUMENT)
    # ##############################

    def open_orders_by_instrument(self, instrument: str, order_type: float = None, callback=None):
        msg = trading.open_orders_by_instrument(instrument=instrument,
                                                order_type=order_type)
        return self.send_request(msg, callback)

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
        return self.send_request(msg, callback)

    # ##############################
    # USER TRADES (GIVEN INSTRUMENT)
    # ##############################

    def user_trades_by_instrument(self, instrument: str, count: int = None, include_old: bool = None, callback=None):
        msg = trading.user_trades_by_instrument(instrument=instrument,
                                                count=count,
                                                include_old=include_old)
        return self.send_request(msg, callback)

    # ##############################
    # ORDER STATUS
    # ##############################

    def order_status(self, order_id: str, callback=None):
        msg = trading.order_status(order_id=order_id)
        return self.send_request(msg, callback)
