"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : business_event.py
Object Type     : Business Event
Layer           : Domain
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from domain.business_event_type import BusinessEventType


@dataclass(slots=True, frozen=True)
class BusinessEvent:

    event_type: BusinessEventType

    company_code: str

    event_date: date

    amount: Decimal

    currency_code: str

    description: str

    cost_center_code: str

    department_code: str

    vat_rate: Decimal

    due_date: date

    customer_code: str | None = None

    supplier_code: str | None = None

    asset_code: str | None = None
    asset_name: str | None = None

    asset_class: str | None = None

    asset_group: str | None = None

    acquisition_cost: Decimal | None = None

    capitalization_date: date | None = None

    depreciation_start_date: date | None = None

    useful_life_months: int | None = None

    depreciation_method: str | None = None

    residual_value: Decimal | None = None

    country_code: str | None = None

    city: str | None = None

    location: str | None = None

    