# Core
import os
import logging
import datetime

import random
import string

# Import networking constants
from deribit.support.networking import *

# Import messages
from deribit.messages.common import message
from deribit.support.endpoints import *

# ##################################################################
# LOGGING
# ##################################################################

# Start logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ##################################################################
# CLASS
# ##################################################################

class DeltaSyncBaseClient(object):

    def __init__(self, key=None, secret=None):

        # This object ID
        self.__id = self.__make_token()

        # Authentication
        self.__key = key
        self.__secret = secret

        # Login management
        self.__is_login = False
        self.__access_token = None
        self.__refresh_token = None
        self.__token_expiry = None

        logging.debug(f"[{self.id}] delta client instance created.")

    # ##################################################################
    # CLASS METHODS
    # ##################################################################

    @classmethod
    def parse_key(cls, key=None):
        key = key or os.getenv('delta_API_KEY', None)
        if not key:
            logger.warning("No delta API key provided to the client.")
        return key

    @classmethod
    def parse_secret(cls, secret=None):
        secret = secret or os.getenv('delta_API_SECRET', None)
        if not secret:
            logger.warning("No delta API secret provided to the client.")
        return secret

    # ##################################################################
    # PROPERTIES
    # ##################################################################

    @property
    def id(self):
        return self.__id

    @property
    def key(self):
        return self.__key

    @property
    def secret(self):
        return self.__secret

    @property
    def access_token(self):
        if not self.__access_token:
            raise Exception("Access token not available.")
        return self.__access_token

    @property
    def token_expiry(self):
        if self.__token_expiry:
            return self.__token_expiry
        return None

    @property
    def token_lifespan(self):
        if self.__token_expiry:
            return self.__token_expiry - datetime.datetime.utcnow()
        return None

    @property
    def is_logged_in(self):
        if not self.__access_token:
            return False
        return True

    def login_required(self):
        return self.__key and self.__secret

    # ##################################################################
    # AUTH MESSAGE FORMULATION
    # ##################################################################

    def __old__login_message(self):
        msg = message(method=SESSION_LOGIN)
        auth_msg = self.auth_with_credentials(msg)
        return auth_msg

    @staticmethod
    def __make_token():
        return ''.join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

    def validate_login(self, message):
        # TODO make some assertion here...
        return True

    def login_message(self):
        return {"jsonrpc": "2.0", "id": self.__make_token(), "method": "public/auth",
                "params": {"grant_type": "client_credentials",
                           "client_id": f"{self.__key}", "client_secret": f"{self.__secret}"}}

    def auth_with_credentials(self, msg):
        if "params" not in msg:
            msg["params"] = {}
        credentials = {"grant_type": "client_credentials",
                       "client_id": self.__key,
                       "client_secret": self.__secret}
        msg["params"] = {**msg["params"], **credentials}
        return msg

    def on_delta_login(self, sender, data=None, websocket=None, **kwargs):
        print("delta auth manager received login signal.")
        return self.parse_login_response(response=data)

    def parse_login_response(self, response, **kwargs):

        if RESP_ERROR in response:
            print(response)
            raise Exception("Failed to obtain token from deribit. Error message received.")

        # Set the tokens
        self.__refresh_token = response[RESP_CONTENT]["refresh_token"]
        self.__access_token = response[RESP_CONTENT]["access_token"]

        # Compute the token expiry datetime
        try:
            lifespan = response[RESP_CONTENT][RESP_CONT_TOK_EXP]
            reference_time = response[RESP_TS_IN]
            expiry_ = datetime.timedelta(seconds=lifespan)
            self.__token_expiry = datetime.datetime.utcfromtimestamp(reference_time / 1000000) + expiry_
            print(f"Token valid until {self.__token_expiry}")

        except:
            # TODO logging here
            pass
