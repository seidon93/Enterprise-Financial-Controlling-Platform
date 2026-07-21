"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : asset.py
Object Type     : Asset Entity
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Enterprise fixed asset master data entity.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(slots=True, frozen=True)
class Asset:
    """
    Enterprise fixed asset master record.
    """

    asset_code: str
    asset_name: str

    asset_category: str

    company_code: str

    supplier_code: str | None

    acquisition_date: date

    acquisition_cost: Decimal

    useful_life_months: int

    depreciation_method: str

    salvage_value: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str

    is_active: bool = True