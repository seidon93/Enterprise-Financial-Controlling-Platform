"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : business_transaction.py
Object Type     : Business Transaction Model
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Represents business data before it is transformed into accounting entries.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(slots=True, frozen=True)
class BusinessTransaction:
    """Business transaction used by generators."""

    company_code: str
    cost_center_code: str
    department_code: str
    currency_code: str

    invoice_date: date
    due_date: date

    amount: Decimal
    vat_rate: Decimal

    description: str