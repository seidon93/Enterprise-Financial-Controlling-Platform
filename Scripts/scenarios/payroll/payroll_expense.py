"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : payroll_expense.py
Object Type     : Payroll Expense Scenario
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates payroll expense accounting entries.
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
from accounting.payroll_accounts import PayrollAccounts
from scenarios.base import AccountingScenario


@dataclass(slots=True, frozen=True)
class PayrollExpenseRequest:
    """
    Input data for payroll expense.
    """

    company_code: str

    employee_code: str

    payroll_date: date

    gross_salary: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str


class PayrollExpenseScenario(AccountingScenario):
    """
    Generates payroll expense journal entry.
    """

    def create(
        self,
        request: PayrollExpenseRequest,
    ) -> JournalEntry:

        document = self.document_generator.create(
            document_type=DocumentType.PAYROLL,
            posting_date=request.payroll_date,
            document_date=request.payroll_date,
            due_date=request.payroll_date,
        )

        entry = JournalEntry(document=document)

        # MD 521
        entry.add_line(
            JournalLine(
                line_number=1,
                account_number=PayrollAccounts.SALARY_EXPENSE,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                employee_code=request.employee_code,
                debit_amount=request.gross_salary,
                credit_amount=Decimal("0.00"),
                amount_local=request.gross_salary,
                description="Payroll Expense",
            )
        )

        # DAL 331
        entry.add_line(
            JournalLine(
                line_number=2,
                account_number=PayrollAccounts.PAYROLL_LIABILITY,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                employee_code=request.employee_code,
                debit_amount=Decimal("0.00"),
                credit_amount=request.gross_salary,
                amount_local=request.gross_salary,
                description="Payroll Liability",
            )
        )

        return self.validate(entry)