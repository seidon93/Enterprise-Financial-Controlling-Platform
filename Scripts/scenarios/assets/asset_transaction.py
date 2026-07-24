"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : asset_transaction.py
Object Type     : Asset Transaction
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Business transaction representing a fixed asset operation.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(slots=True, frozen=True)
class AssetTransaction:
    """
    Enterprise asset business transaction.
    """

    company_code: str

    asset_code: str
    asset_name: str
    asset_class: str
    asset_group: str

    supplier_code: str | None

    acquisition_date: date

    acquisition_cost: Decimal

    vat_rate: Decimal

    useful_life_months: int

    depreciation_method: str

    residual_value: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str