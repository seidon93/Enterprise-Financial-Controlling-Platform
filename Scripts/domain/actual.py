"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : actual.py
Object Type     : Domain Model
Layer           : Domain
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True, frozen=True)
class Actual:

    company_code: str

    fiscal_year: int

    fiscal_period: int

    cost_center_code: str

    account_number: str

    amount: Decimal