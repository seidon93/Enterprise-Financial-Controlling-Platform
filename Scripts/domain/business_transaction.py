"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : business_transaction.py
Object Type     : Domain Model
Layer           : Domain Layer
Version         : 2.0.0
Status          : Development
Description     : Business transaction model used by business generators.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(slots=True, frozen=True)
class BusinessTransaction:
    """
    Business transaction used by business data generators.

    The transaction keeps both the aggregated monetary amount and the
    underlying commercial drivers required for controller analytics:

        amount = quantity * unit_price

    Product, quantity and unit price enable downstream Price / Volume /
    Mix analysis without changing the accounting journal model.
    """

    company_code: str
    cost_center_code: str
    department_code: str
    currency_code: str

    invoice_date: date
    due_date: date

    amount: Decimal
    vat_rate: Decimal

    description: str

    product_code: str | None = None
    quantity: Decimal | None = None
    unit_price: Decimal | None = None

    customer_code: str | None = None
    supplier_code: str | None = None