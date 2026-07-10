"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
Shared Constants
===============================================================================
"""

from __future__ import annotations

from datetime import date


VALID_FROM = date(2020, 1, 1)
VALID_TO = date(2099, 12, 31)


LEGAL_FORMS = {
    "CZ": "s.r.o.",
    "SK": "s.r.o.",
    "DE": "GmbH",
    "AT": "GmbH",
    "PL": "Sp. z o.o.",
}


BUSINESS_UNITS = {
    "CZ": "Central Europe",
    "SK": "Central Europe",
    "DE": "DACH",
    "AT": "DACH",
    "PL": "Eastern Europe",
}