"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : income_tax_accrual.py
Object Type     : Income Tax Accrual Scenario
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting entries for corporate income tax accrual.
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
class IncomeTaxAccrualRequest:
    """
    Input data for income tax accrual.
    """

    company_code: str

    closing_date: date

    amount: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str

    tax_expense_account: str

    tax_liability_account: str


class IncomeTaxAccrualScenario(AccountingScenario):
    """
    Generates accounting entries for income tax accrual.
    """

    def create(
        self,
        request: IncomeTaxAccrualRequest,
    ) -> JournalEntry:

        document = self.document_generator.create(
            document_type=DocumentType.CLOSING,
            posting_date=request.closing_date,
            document_date=request.closing_date,
            due_date=request.closing_date,
        )

        entry = JournalEntry(document=document)

        # MD Income Tax Expense

        entry.add_line(

            JournalLine(

                line_number=1,

                account_number=request.tax_expense_account,

                company_code=request.company_code,

                cost_center_code=request.cost_center_code,

                department_code=request.department_code,

                currency_code=request.currency_code,

                debit_amount=request.amount,

                credit_amount=Decimal("0.00"),

                amount_local=request.amount,

                description="Income Tax Accrual",
            )
        )

        # DAL Income Tax Liability

        entry.add_line(

            JournalLine(

                line_number=2,

                account_number=request.tax_liability_account,

                company_code=request.company_code,

                cost_center_code=request.cost_center_code,

                department_code=request.department_code,

                currency_code=request.currency_code,

                debit_amount=Decimal("0.00"),

                credit_amount=request.amount,

                amount_local=request.amount,

                description="Income Tax Payable",
            )
        )

        return self.validate(entry)