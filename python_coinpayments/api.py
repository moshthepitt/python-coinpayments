# -*- coding: utf-8 -*-
"""
Coinpayments module
"""
import hashlib
import hmac
import json
import urllib.error
import urllib.parse
import urllib.request


def calculate_hmac(secret: str, **params):
    """
    Calculate the HMAC based on the secret and url encoded params
    """
    encoded = urllib.parse.urlencode(params).encode("utf-8")
    return hmac.new(bytearray(secret, "utf-8"), encoded,
                    hashlib.sha512).hexdigest()


def authenticate_ipn_request(
        secret: str,
        merchant_id: str,
        http_headers: dict,
        http_post: dict,
        ipn_mode: str = "hmac",
):
    """
    Authenticates the IPN request

    Returns a tuple of:
        - bool indicating if authenticated or not
        - error message, if any
    """
    params = http_post
    received_ipn_mode = params.get("ipn_mode")
    merchant = params.get("merchant")
    http_hmac = http_headers.get("HTTP_HMAC")
    hashed = calculate_hmac(secret=secret, **params)

    if merchant is None:
        result = False, "No merchant ID"
    elif merchant != merchant_id:
        result = False, "Invalid merchant ID"
    elif received_ipn_mode is None:
        result = False, "No ipn_mode"
    elif received_ipn_mode != ipn_mode:
        result = False, "Invalid ipn_mode"
    elif http_hmac is None:
        result = False, "No HTTP HMAC"
    elif http_hmac != hashed:
        result = False, "Invalid HTTP HMAC"
    else:
        result = True, None

    return result


class CoinPayments:
    """
    Coinpayments API handler class

    https://www.coinpayments.net/
    """

    def __init__(self, public_key: str, private_key: str, ipn_url: str = ""):
        """
        Initialize!
        """
        self.url = "https://www.coinpayments.net/api.php"
        self.public_key = public_key
        self.private_key = private_key
        self.ipn_url = ipn_url
        self.format = "json"
        self.version = 1

    def _package_params(self, params: dict = None):
        """
        Helper to package params (for DRYness)
        """
        if params is None:
            params = {}

        params.update({
            "key": self.public_key,
            "version": self.version,
            "format": self.format
        })

        return params

    def create_hmac(self, **params):
        """
        Generate an HMAC based upon the url arguments/parameters
        We generate the encoded url here and return it to request because
        the hmac on both sides depends upon the order of the parameters, any
        change in the order and the hmacs wouldn't match
        """
        encoded = urllib.parse.urlencode(params).encode("utf-8")
        return encoded, calculate_hmac(secret=self.private_key, **params)

    def request(self, request_method: str, **params):
        """
        The basic request that all API calls use
        the parameters are joined in the actual api methods so the parameter
        strings can be passed and merged inside those methods instead of the
        request method
        """
        encoded, sig = self.create_hmac(**params)

        headers = {"Hmac": sig}

        if request_method == "get":
            req = urllib.request.Request(self.url, headers=headers)
        elif request_method == "post":
            headers["Content-type"] = "application/x-www-form-urlencoded"
            req = urllib.request.Request(
                self.url, data=encoded, headers=headers)
        try:
            response = urllib.request.urlopen(req)
        except urllib.error.HTTPError as exception:
            response_body = exception.read()
        else:
            response_body = response.read()

        return json.loads(response_body)

    def create_transaction(self, params: dict = None):
        """
        Creates a transaction to give to the purchaser
        https://www.coinpayments.net/apidoc-create-transaction
        """
        params = self._package_params(params)

        if self.ipn_url:
            params.update({"ipn_url": self.ipn_url})

        params.update({"cmd": "create_transaction"})

        return self.request("post", **params)

    def get_basic_info(self, params: dict = None):
        """
        Gets merchant info based on API key (callee)
        https://www.coinpayments.net/apidoc-get-basic-info
        """
        params = self._package_params(params)
        params.update({"cmd": "get_basic_info"})

        return self.request("post", **params)

    def rates(self, params: dict = None):
        """
        Gets current rates for currencies
        https://www.coinpayments.net/apidoc-rates
        """
        params = self._package_params(params)
        params.update({"cmd": "rates"})

        return self.request("post", **params)

    def balances(self, params: dict = None):
        """
        Get current wallet balances
        https://www.coinpayments.net/apidoc-balances
        """
        params = self._package_params(params)
        params.update({"cmd": "balances"})

        return self.request("post", **params)

    def get_deposit_address(self, params: dict = None):
        """
        Get address for personal deposit use
        https://www.coinpayments.net/apidoc-get-deposit-address
        """
        params = self._package_params(params)
        params.update({"cmd": "get_deposit_address"})

        return self.request("post", **params)

    def get_callback_address(self, params: dict = None):
        """
        Get a callback address to recieve info about address status
        https://www.coinpayments.net/apidoc-get-callback-address
        """
        params = self._package_params(params)
        if self.ipn_url:
            params.update({"ipn_url": self.ipn_url})
        params.update({"cmd": "get_callback_address"})

        return self.request("post", **params)

    def create_transfer(self, params: dict = None):
        """
        Not really sure why this function exists to be honest, it transfers
        coins from your addresses to another account on coinpayments using
        merchant ID
        https://www.coinpayments.net/apidoc-create-transfer
        """
        params = self._package_params(params)
        params.update({"cmd": "create_transfer"})

        return self.request("post", **params)

    def create_withdrawal(self, params: dict = None):
        """
        Withdraw coins to a specified address,
        optionally set a IPN when complete.
        https://www.coinpayments.net/apidoc-create-withdrawal
        """
        params = self._package_params(params)
        params.update({"cmd": "create_withdrawal"})

        return self.request("post", **params)

    def convert_coins(self, params: dict = None):
        """
        Convert your balances from one currency to another
        https://www.coinpayments.net/apidoc-convert
        """
        params = self._package_params(params)
        params.update({"cmd": "convert"})

        return self.request("post", **params)

    def get_conversion_limits(self, params: dict = None):
        """
        Get Conversion Limits
        https://www.coinpayments.net/apidoc-convert-limits
        """
        params = self._package_params(params)
        params.update({"cmd": "convert_limits"})

        return self.request("post", **params)

    def get_withdrawal_history(self, params: dict = None):
        """
        Get list of recent withdrawals (1-100max)
        https://www.coinpayments.net/apidoc-get-withdrawal-history
        """
        params = self._package_params(params)
        params.update({"cmd": "get_withdrawal_history"})

        return self.request("post", **params)

    def get_withdrawal_info(self, params: dict = None):
        """
        Get information about a specific withdrawal based on withdrawal ID
        https://www.coinpayments.net/apidoc-get-withdrawal-info
        """
        params = self._package_params(params)
        params.update({"cmd": "get_withdrawal_info"})

        return self.request("post", **params)

    def get_conversion_info(self, params: dict = None):
        """
        Get information about a specific conversion based on conversion ID
        https://www.coinpayments.net/apidoc-get-conversion-info
        """
        params = self._package_params(params)
        params.update({"cmd": "get_conversion_info"})

        return self.request("post", **params)

    def get_tx_info(self, params: dict = None):
        """
        Get Transaction Information based on transaction ID

        Note: It is recommended to handle IPNs instead of using this command
        when possible, it is more efficient and places less load on
        CoinPayments servers.
        https://www.coinpayments.net/apidoc-get-tx-info
        """
        params = self._package_params(params)
        params.update({"cmd": "get_tx_info"})

        return self.request("post", **params)

    def get_tx_info_multi(self, params: dict = None):
        """
        Get Multiple Transaction Information

        Lets you query up to 25 transaction ID(s)
        (API key must belong to the seller.) Transaction IDs should be
        separated with a | (pipe symbol.)

        Note: It is recommended to handle IPNs instead of using this command
        when possible, it is more efficient and places less load on
        CoinPayments servers.
        https://www.coinpayments.net/apidoc-get-tx-info
        """
        params = self._package_params(params)
        params.update({"cmd": "get_tx_info_multi"})

        return self.request("post", **params)

    def get_tx_list(self, params: dict = None):
        """
        Get Transaction IDs
        https://www.coinpayments.net/apidoc-get-tx-ids
        """
        params = self._package_params(params)
        params.update({"cmd": "get_tx_ids"})

        return self.request("post", **params)
