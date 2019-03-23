"""
Tests for the pesa app
"""
from decimal import Decimal
from unittest.mock import MagicMock, patch

from python_coinpayments import (CoinPayments, authenticate_ipn_request,
                                 calculate_hmac)

CLIENT = CoinPayments(
    public_key="public key",
    private_key="private key",
    ipn_url="https://example.com")


class TestCoinPayments:
    """
    Test class for CoinPayments
    """

    def test_init(self):
        """
        Test that CoinPayments initializes correctly
        """
        assert "private key" == CLIENT.private_key
        assert "public key" == CLIENT.public_key
        assert "https://example.com" == CLIENT.ipn_url
        assert "json" == CLIENT.format
        assert 1 == CLIENT.version

    def test_package_params(self):
        """
        Test that _package_params works
        """
        input_params = {"hello": "world", "foo": "bar"}
        assert {
            "hello": "world",
            "key": CLIENT.public_key,
            "version": CLIENT.version,
            "format": CLIENT.format,
            "foo": "bar",
        } == CLIENT._package_params(input_params)

    def test_calculate_hmac(self):
        """
        Test calculate_hmac
        """
        params = {"foo": "bar"}
        secret_key = "i love oov"
        assert (
            "a2367a3768a4e7e46bf4c47f54c1781c758d5441d5573caf86f3ac9b71b5125f3"
            "eb36cf63d8dc790cec1a63554e9a70ae69b3d802879cbc8fe85b3b7f876f1d7"
            == calculate_hmac(secret=secret_key, **params))

    def test_authenticate_ipn_request(self):
        """
        Test authenticate_ipn_request
        """
        params = dict(
            ipn_version="1.0",
            ipn_id="ce041097ff2647f3c01375eacdc90e1d",
            ipn_mode="hmac",
            merchant="8d683f17575a9544c6180206f52d4a9c",
            ipn_type="api",
            txn_id="CPCH5TRXAUDLO6ANAV2UCKDFN2",
            status="0",
            status_text="Waiting for buyer funds...",
            currency1="USD",
            currency2="BTC",
            amount1="1",
            amount2="1",
            fee="0.006",
            buyer_name="CoinPayments API",
            invoice="128fee28-2d37-448e-a339-71980a8950c1",
            received_amount="0",
            received_confirms="0",
        )
        secret_key = "mosh"
        hmac = "8c38725cfa6175938c216beecfd6b56284590b857a27fe4c0ad2438aa88e3d8289aa493c7f9e7a5a721c34b92de5c31c5f7534f215a9c17f1121c29508634861"  # noqa

        # test successful
        assert (authenticate_ipn_request(
            secret=secret_key,
            merchant_id="8d683f17575a9544c6180206f52d4a9c",
            http_headers={"HTTP_HMAC": hmac},
            http_post=params,
        )[0] is True)

        # no hmac
        authenticator = authenticate_ipn_request(
            secret=secret_key,
            merchant_id="8d683f17575a9544c6180206f52d4a9c",
            http_headers={"sthing": hmac},
            http_post=params,
        )
        assert authenticator[0] is False
        assert "No HTTP HMAC" == authenticator[1]

        # wrong hmac
        authenticator = authenticate_ipn_request(
            secret=secret_key,
            merchant_id="8d683f17575a9544c6180206f52d4a9c",
            http_headers={"HTTP_HMAC": "wrong"},
            http_post=params,
        )
        assert authenticator[0] is False
        assert "Invalid HTTP HMAC" == authenticator[1]

        # no merchant id
        m_params = params.copy()
        m_params.pop("merchant")
        authenticator = authenticate_ipn_request(
            secret=secret_key,
            merchant_id="8d683f17575a9544c6180206f52d4a9c",
            http_headers={"HTTP_HMAC": hmac},
            http_post=m_params,
        )
        assert authenticator[0] is False
        assert "No merchant ID" == authenticator[1]

        # wrong merchant id
        m_params["merchant"] = "wrong"
        authenticator = authenticate_ipn_request(
            secret=secret_key,
            merchant_id="8d683f17575a9544c6180206f52d4a9c",
            http_headers={"HTTP_HMAC": hmac},
            http_post=m_params,
        )
        assert authenticator[0] is False
        assert "Invalid merchant ID" == authenticator[1]

        # no ipn mode
        i_params = params.copy()
        i_params.pop("ipn_mode")
        authenticator = authenticate_ipn_request(
            secret=secret_key,
            merchant_id="8d683f17575a9544c6180206f52d4a9c",
            http_headers={"HTTP_HMAC": hmac},
            http_post=i_params,
        )
        assert authenticator[0] is False
        assert "No ipn_mode" == authenticator[1]

        # wrong ipn_mode
        i_params["ipn_mode"] = "wrong"
        authenticator = authenticate_ipn_request(
            secret=secret_key,
            merchant_id="8d683f17575a9544c6180206f52d4a9c",
            http_headers={"HTTP_HMAC": hmac},
            http_post=i_params,
        )
        assert authenticator[0] is False
        assert "Invalid ipn_mode" == authenticator[1]

    def test_create_hmac(self):
        """
        Test create_hmac
        """
        params = CLIENT._package_params({"foo": "bar"})
        encoded, sig = CLIENT.create_hmac(**params)
        assert b"foo=bar&key=public+key&version=1&format=json" == encoded
        assert (
            "d49793b8bf7492a04d709546085b3bb933e37ab4522eea4c131ee68c299e335dc"
            "2ae6db1e21f75711a851575e64fe625772e8cf0323c1819efe63e6b0e98c97b"
            == sig)

    @patch.object(CoinPayments, "request")
    def test_create_transaction(self, mocked_request):
        """
        Test create_transaction
        """
        params = dict(
            amount=Decimal(10),
            currency1="USD",
            currency2="BTC",
            buyer_email="johndoe@example.com",
            address="SellerBitcoinAddress",
            buyer_name="John Doe",
            item_name="Investment",
            item_number=1337,
            invoice="invoice-1337",
            custom="custom-field-1337",
            ipn_url="https://example.com",
        )
        CLIENT.create_transaction(params=params)
        # get final_params
        params.update({
            "key": CLIENT.public_key,
            "version": CLIENT.version,
            "format": CLIENT.format,
        })
        mocked_request.assert_called_once_with("post", **params)

    @patch.object(CoinPayments, "request")
    def test_get_basic_info(self, mocked_request):
        """
        Test get_basic_info
        """
        params = {}
        CLIENT.get_basic_info(params=params)
        # get final_params
        params.update({
            "key": CLIENT.public_key,
            "version": CLIENT.version,
            "format": CLIENT.format,
        })
        mocked_request.assert_called_once_with("post", **params)

    @patch.object(CoinPayments, "request")
    def test_rates(self, mocked_request):
        """
        Test rates
        """
        params = {}
        CLIENT.rates(params=params)
        # get final_params
        params.update({
            "key": CLIENT.public_key,
            "version": CLIENT.version,
            "format": CLIENT.format,
        })
        mocked_request.assert_called_once_with("post", **params)

    @patch.object(CoinPayments, "request")
    def test_get_withdrawal_history(self, mocked_request):
        """
        Test get_withdrawal_history
        """
        params = {}
        CLIENT.get_withdrawal_history(params=params)
        # get final_params
        params.update({
            "key": CLIENT.public_key,
            "version": CLIENT.version,
            "format": CLIENT.format,
        })
        mocked_request.assert_called_once_with("post", **params)

    @patch.object(CoinPayments, "request")
    def test_get_deposit_address(self, mocked_request):
        """
        Test get_deposit_address
        """
        params = {"currency": "BTC"}
        CLIENT.get_deposit_address(params=params)
        # get final_params
        params.update({
            "key": CLIENT.public_key,
            "version": CLIENT.version,
            "format": CLIENT.format,
        })
        mocked_request.assert_called_once_with("post", **params)

    @patch.object(CoinPayments, "request")
    def test_balances(self, mocked_request):
        """
        Test balances
        """
        params = {"all": 1}
        CLIENT.balances(params=params)
        # get final_params
        params.update({
            "key": CLIENT.public_key,
            "version": CLIENT.version,
            "format": CLIENT.format,
        })
        mocked_request.assert_called_once_with("post", **params)

    @patch.object(CoinPayments, "request")
    def test_create_withdrawal(self, mocked_request):
        """
        Test create_withdrawal
        """
        params = dict(
            amount=Decimal(10),
            currency="BTC",
            currency2="USD",
            address="DepositBitcoinAddress",
            note="The note",
            ipn_url="https://example.com",
        )
        CLIENT.create_withdrawal(params=params)
        # get final_params
        params.update({
            "key": CLIENT.public_key,
            "version": CLIENT.version,
            "format": CLIENT.format,
        })
        mocked_request.assert_called_once_with("post", **params)

    @patch("python_coinpayments.api.urllib.request.urlopen")
    def test_request(self, mocked_request):
        """
        Test the request method
        """
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = """
            {
                "error": "ok",
                "result": {
                    "id": "hex string",
                    "status": 0,
                    "amount": 1.00
                }
            }"""
        cm.__enter__.return_value = cm
        mocked_request.return_value = cm

        params = dict(
            amount=Decimal(10),
            currency1="BTC",
            currency2="USD",
            address="DepositBitcoinAddress",
            note="The note",
            ipn_url="https://example.com",
        )

        encoded, sig = CLIENT.create_hmac(**params)
        headers = {
            "Hmac": sig,
            "Content-type": "application/x-www-form-urlencoded"
        }
        CLIENT.request("post", **params)

        assert 1 == mocked_request.call_count
        args, kwargs = mocked_request.call_args_list[0]
        request = args[0]

        assert headers == request.headers
        assert encoded == request.data
        assert "https://www.coinpayments.net/api.php" == request.full_url
