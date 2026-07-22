"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : asset.py
Object Type     : Asset Entity
Layer           : Domain
Version         : 2.0.0
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

    # -------------------------------------------------------------------------
    # Identification
    # -------------------------------------------------------------------------

    asset_code: str
    asset_name: str
    asset_class: str
    asset_group: str

    # -------------------------------------------------------------------------
    # Organization
    # -------------------------------------------------------------------------

    company_code: str
    currency_code: str

    cost_center_code: str
    department_code: str


    # -------------------------------------------------------------------------
    # Acquisition
    # -------------------------------------------------------------------------

    acquisition_date: date
    capitalization_date: date
    depreciation_start_date: date

    acquisition_cost: Decimal
    # -------------------------------------------------------------------------
    # Depreciation
    # -------------------------------------------------------------------------

    useful_life_months: int
    depreciation_method: str

    # -------------------------------------------------------------------------
    # Location
    # -------------------------------------------------------------------------

    country_code: str
    city: str
    location: str


    residual_value: Decimal = Decimal("0.00")

    vat_rate: Decimal = Decimal("0.21")


    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    is_active: bool = True
    disposal_date: date | None = None

    supplier_code: str | None = None