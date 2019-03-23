# -*- coding: utf-8 -*-
"""Top-level package for Python CoinPayments."""

__author__ = """Kelvin Jayanoris"""
__email__ = "kelvin@jayanoris.com"
__version__ = "0.5.0"

# pylint: disable=unused-import
from python_coinpayments.api import (  # noqa
    CoinPayments, authenticate_ipn_request, calculate_hmac,
)
