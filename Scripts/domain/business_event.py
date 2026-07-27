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

    material_code: str | None = None

    material_name: str | None = None

    warehouse_code: str | None = None

    storage_location: str | None = None

    quantity: Decimal | None = None

    unit_price: Decimal | None = None

    source_warehouse: str | None = None

    target_warehouse: str | None = None

    inventory_code: str | None = None

    unit_cost: Decimal | None = None

    from_cost_center_code: str | None = None
    from_department_code: str | None = None
    to_cost_center_code: str | None = None
    to_department_code: str | None = None

    employee_code: str | None = None

    gross_salary: Decimal | None = None

    employer_contribution: Decimal | None = None

    employee_tax: Decimal | None = None

    bonus_amount: Decimal | None = None

    overtime_amount: Decimal | None = None

    vacation_accrual: Decimal | None = None

    payroll_date: date | None = None    

    tax_amount: Decimal | None = None

    payment_amount: Decimal | None = None

