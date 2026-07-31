"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : prepaid_expense.py
Object Type     : Prepaid Expense Scenario
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting entries for prepaid expenses.
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
class PrepaidExpenseRequest:
    """
    Input data for prepaid expense.
    """

    company_code: str

    closing_date: date

    amount: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str

    expense_account: str


class PrepaidExpenseScenario(AccountingScenario):
    """
    Generates accounting entries for prepaid expenses.
    """

    def create(
        self,
        request: PrepaidExpenseRequest,
    ) -> JournalEntry:

        document = self.document_generator.create(
            document_type=DocumentType.CLOSING,
            posting_date=request.closing_date,
            document_date=request.closing_date,
            due_date=request.closing_date,
        )

        entry = JournalEntry(document=document)

        # MD 381
        entry.add_line(
            JournalLine(
                line_number=1,
                account_number=ClosingAccounts.PREPAID_EXPENSES,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=request.amount,
                credit_amount=Decimal("0.00"),
                amount_local=request.amount,
                description="Prepaid Expense",
            )
        )

        # DAL 5xx
        entry.add_line(
            JournalLine(
                line_number=2,
                account_number=request.expense_account,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=Decimal("0.00"),
                credit_amount=request.amount,
                amount_local=request.amount,
                description="Expense Adjustment",
            )
        )

        return self.validate(entry)