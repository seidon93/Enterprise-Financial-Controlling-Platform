"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : inventory.py
Object Type     : Inventory Transaction
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Represents one inventory transaction.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


@dataclass(slots=True, frozen=True)
class Inventory:

    company_code: str

    material_code: str
    material_name: str

    warehouse_code: str
    storage_location: str

    movement_date: date

    quantity: Decimal

    unit_price: Decimal

    total_amount: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str

    supplier_code: str | None = None

    customer_code: str | None = None

    source_warehouse: str | None = None

    target_warehouse: str | None = None

    country_code: str | None = None

    city: str | None = None

    location: str | None = None