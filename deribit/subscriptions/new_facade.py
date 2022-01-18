import logging

# from deribit.requests.client import DeltaSyncRequestClient as RequestClient

# THIS IS FIRST ATTEMPT
from deribit.subscriptions.new_req import RequestClient
from deribit.subscriptions.new_sub import SubscriptionClient

# THIS IS SECOND ATTEMPT
# from deribit.subscriptions.new_mix_both import UnifiedClient
from deribit.unified.requests import RequestClient

from deribit.subscriptions.clients import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DeltaApiClient(object):

    def __init__(self, url, key, secret, req_kwargs=None, sub_kwargs=None):

        self.__url = url
        self.__key = key
        self.__secret = secret

        # Init request client
        self.__req_kwargs = req_kwargs
        self.__request_client = None

        # Init sub clients
        self.__sub_kwargs = sub_kwargs
        self.__quotes_subscription = None           ## -------> TODO FACTORY !!!!!!!!!1
        self.__orderbooks_subscription = None

    @property
    def request(self):
        if not self.__request_client:
            self.__request_client = RequestClient(url=self.__url, key=self.__key, secret=self.__secret)
        return self.__request_client

    @property
    def quotes(self):
        if not self.__quotes_subscription:
            raise NotImplementedError()
            # self.__quotes_subscription = DeltaQuotes()
        return self.__quotes_subscription

    @property
    def orderbooks(self):
        if not self.__orderbooks_subscription:
            raise NotImplementedError()
            # self.__orderbooks_subscription = DeltaOrderbooks()
        return self.__orderbooks_subscription
