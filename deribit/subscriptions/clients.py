import time

from .base import DeltaWebsocketClient
from .events import quotes, orderbooks

from utilities.marshal import to_list


# ####################################################################
# delta SUBSCRIPTION CLIENT -- BASE CLASS
# ####################################################################

class DeltaSubscriptionClient(DeltaWebsocketClient):

    def __init__(self, callback, data_type, key=None, secret=None):

        # Type of data handle by this client
        self.__data_type = data_type

        # Keeping track
        self.__channels = []

        super().__init__(callback=callback, key=key, secret=secret)

    def __del__(self):
        try:
            self._ws.safe_close()
        except:
            pass

    # ####################################################################
    # PUBLIC METHODS
    # ####################################################################

    def subscribe(self, channels, retry=0):

        # Sanitize new channels and build message
        new_channels = to_list(channels)
        id, msg = self.__make_message(new_channels, subscribe=True)

        # Publish
        self.add_to_pending(id=id, message=msg)

        # Log the information
        these_names = ",".join(new_channels)
        print(f"[{id}] Subscribing to: {these_names}.")

        # Perform subscription
        try:
            self.send_message(msg)
            self.__channels = list(set(self.__channels + new_channels))

        except KeyboardInterrupt:
            pass

        except:
            time.sleep(min(10.0, 2**retry))
            self.restart(callback=self.subscribe, channels=channels, retry=retry+1)

        finally:
            self.scheduler.enter(5, 1, self._purge)

    def unsubscribe(self, channels):
        channels = to_list(channels)
        msg = self.__make_message(channels, subscribe=False)
        for c in channels:
            try:
                self.__channels.remove(c)
            except:
                pass
        # Execute
        self.send_message(msg)

    def __make_message(self, channels, subscribe=True):
        id_ = self.make_id_token()
        sub_ = "subscribe" if subscribe else "unsubscribe"
        type_ = self.__data_type
        channels = [f"{type_}.{c}" for c in channels]
        return id_, {"jsonrpc": "2.0", "id": id_, "method": f"public/{sub_}", "params": {"channels": channels}}


# ##################################################################
# QUOTES CLASS
# ##################################################################

class DeltaQuotes(DeltaSubscriptionClient):

    def __init__(self, callback=None, key=None, secret=None):

        def broadcast(message):
            quotes.send(message)

        callback = callback or broadcast
        super().__init__(callback=callback, key=key, secret=secret, data_type="quote")


# ##################################################################
# ORDERBOOKS CLASS
# ##################################################################

class DeltaOrderbooks(DeltaSubscriptionClient):

    def __init__(self, callback=None):

        def broadcast(message):
            orderbooks.send(message)

        callback = callback or broadcast
        super().__init__(callback=callback, key=None, secret=None, data_type="book")

