"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : variance.py
Object Type     : Domain Model
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Budget vs Actual variance model.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True, frozen=True)
class Variance:

    company_code: str

    fiscal_year: int

    fiscal_period: int

    cost_center_code: str

    account_number: str

    budget: Decimal

    actual: Decimal

    variance: Decimal

    variance_percent: Decimal

    favorable: bool