"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : asset_event.py
Object Type     : Asset Business Event
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Represents a business event related to enterprise fixed assets.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from domain.business_event_type import BusinessEventType


@dataclass(slots=True, frozen=True)
class AssetEvent:
    """
    Enterprise asset business event.
    """

    event_type: BusinessEventType

    company_code: str

    asset_code: str
    asset_name: str
    asset_category: str

    supplier_code: str | None

    event_date: date

    acquisition_cost: Decimal

    vat_rate: Decimal

    useful_life_months: int

    depreciation_method: str

    salvage_value: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str