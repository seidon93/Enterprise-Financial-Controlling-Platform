"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : customer.py
Object Type     : Domain Model
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Enterprise customer master data model.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(slots=True, frozen=True)
class Customer:
    """
    Enterprise customer master record.
    """

    customer_code: str
    customer_name: str

    customer_type: str

    country_code: str
    city: str

    industry: str

    payment_terms: int

    credit_limit: Decimal

    risk_category: str

    active_from: date
    active_to: date

    is_active: bool