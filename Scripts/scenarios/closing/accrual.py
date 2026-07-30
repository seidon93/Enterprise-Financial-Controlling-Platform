"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : accrual.py
Object Type     : Accrual Scenario
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting entries for accruals.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from accounting.enums import DocumentType
from accounting.models import JournalEntry, JournalLine
from scenarios.base import AccountingScenario

from accounting.closing_accounts import ClosingAccounts


@dataclass(slots=True, frozen=True)
class AccrualRequest:
    """
    Input data for accrual posting.
    """

    company_code: str

    closing_date: date

    amount: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str