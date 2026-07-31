"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : accrued_revenue.py
Object Type     : Accrued Revenue Scenario
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting entries for accrued revenue.
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
from accounting.closing_accounts import ClosingAccounts

from scenarios.base import AccountingScenario


@dataclass(slots=True, frozen=True)
class AccruedRevenueRequest:
    """
    Input data for accrued revenue.
    """

    company_code: str

    closing_date: date

    amount: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str

    revenue_account: str


class AccruedRevenueScenario(AccountingScenario):
    """
    Generates accounting entries for accrued revenue.
    """

    def create(
        self,
        request: AccruedRevenueRequest,
    ) -> JournalEntry:

        document = self.document_generator.create(
            document_type=DocumentType.CLOSING,
            posting_date=request.closing_date,
            document_date=request.closing_date,
            due_date=request.closing_date,
        )

        entry = JournalEntry(document=document)

        # MD 388 – Estimated Receivables
        entry.add_line(
            JournalLine(
                line_number=1,
                account_number=ClosingAccounts.ESTIMATED_RECEIVABLES,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=request.amount,
                credit_amount=Decimal("0.00"),
                amount_local=request.amount,
                description="Accrued Revenue",
            )
        )

        # DAL 6xx – Revenue
        entry.add_line(
            JournalLine(
                line_number=2,
                account_number=request.revenue_account,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=Decimal("0.00"),
                credit_amount=request.amount,
                amount_local=request.amount,
                description="Accrued Revenue",
            )
        )

        return self.validate(entry)