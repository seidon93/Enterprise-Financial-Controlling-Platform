"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : bad_debt_allowance.py
Object Type     : Bad Debt Allowance Scenario
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting entries for bad debt allowance.
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


@dataclass(slots=True, frozen=True)
class BadDebtAllowanceRequest:
    """
    Input data for bad debt allowance.
    """

    company_code: str

    closing_date: date

    amount: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str

    expense_account: str

    allowance_account: str


class BadDebtAllowanceScenario(AccountingScenario):
    """
    Generates accounting entries for bad debt allowance.
    """

    def create(
        self,
        request: BadDebtAllowanceRequest,
    ) -> JournalEntry:

        document = self.document_generator.create(
            document_type=DocumentType.CLOSING,
            posting_date=request.closing_date,
            document_date=request.closing_date,
            due_date=request.closing_date,
        )

        entry = JournalEntry(document=document)

        # MD Expense

        entry.add_line(

            JournalLine(

                line_number=1,

                account_number=request.expense_account,

                company_code=request.company_code,

                cost_center_code=request.cost_center_code,

                department_code=request.department_code,

                currency_code=request.currency_code,

                debit_amount=request.amount,

                credit_amount=Decimal("0.00"),

                amount_local=request.amount,

                description="Bad Debt Allowance",
            )
        )

        # DAL Allowance

        entry.add_line(

            JournalLine(

                line_number=2,

                account_number=request.allowance_account,

                company_code=request.company_code,

                cost_center_code=request.cost_center_code,

                department_code=request.department_code,

                currency_code=request.currency_code,

                debit_amount=Decimal("0.00"),

                credit_amount=request.amount,

                amount_local=request.amount,

                description="Allowance for Doubtful Receivables",
            )
        )

        return self.validate(entry)