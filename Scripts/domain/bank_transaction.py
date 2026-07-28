"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : bank_transaction.py
Object Type     : Bank Transaction Business Object
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Represents banking and treasury transaction.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(slots=True, frozen=True)
class BankTransaction:
    """
    Enterprise bank transaction.
    """

    company_code: str

    bank_account: str

    transaction_date: date

    amount: Decimal

    currency_code: str

    description: str

    transaction_type: str

    cost_center_code: str

    department_code: str

    loan_term: str  # "SHORT" | "LONG"
    
    customer_code: str | None = None

    supplier_code: str | None = None

    reference_number: str | None = None

    