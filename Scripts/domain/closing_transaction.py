"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : closing_transaction.py
Object Type     : Closing Business Object
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Represents period-end closing transaction.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(slots=True, frozen=True)
class ClosingTransaction:
    """
    Enterprise period-end closing transaction.
    """

    company_code: str

    closing_date: date

    amount: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str

    closing_type: str

    description: str

    expense_account: str | None = None

    revenue_account: str | None = None

    balance_account: str | None = None

    provision_account: str | None = None

    inventory_account: str | None = None

    allowance_account: str | None = None

    debit_account: str | None = None

    credit_account: str | None = None

    tax_expense_account: str | None = None

    tax_liability_account: str | None = None

    deferred_tax_expense_account: str | None = None

    deferred_tax_balance_account: str | None = None

    profit_account: str | None = None

    retained_earnings_account: str | None = None

    opening_account: str | None = None