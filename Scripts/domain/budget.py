"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : budget.py
Object Type     : Domain Model
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Budget value for management reporting.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True, frozen=True)
class Budget:

    company_code: str

    fiscal_year: int

    fiscal_period: int

    cost_center_code: str

    account_number: str

    amount: Decimal