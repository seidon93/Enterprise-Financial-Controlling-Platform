"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : payroll_tax.py
Object Type     : Payroll Tax Scenario
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting entries for payroll tax withholding.
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
class PayrollTaxRequest:
    """
    Input data for payroll tax.
    """

    company_code: str

    employee_code: str

    payroll_date: date

    tax_amount: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str


class PayrollTaxScenario(AccountingScenario):
    """
    Generates payroll tax journal entries.
    """

    def create(
        self,
        request: PayrollTaxRequest,
    ) -> JournalEntry:

        document = self.document_generator.create(
            document_type=DocumentType.PAYROLL,
            posting_date=request.payroll_date,
            document_date=request.payroll_date,
            due_date=request.payroll_date,
        )

        entry = JournalEntry(document=document)

        # MD 331
        entry.add_line(
            JournalLine(
                line_number=1,
                account_number=PayrollAccounts.PAYROLL_LIABILITY,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                employee_code=request.employee_code,
                debit_amount=request.tax_amount,
                credit_amount=Decimal("0.00"),
                amount_local=request.tax_amount,
                description="Payroll Tax Withholding",
            )
        )

        # DAL 342
        entry.add_line(
            JournalLine(
                line_number=2,
                account_number=PayrollAccounts.PAYROLL_TAX,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                employee_code=request.employee_code,
                debit_amount=Decimal("0.00"),
                credit_amount=request.tax_amount,
                amount_local=request.tax_amount,
                description="Payroll Tax Liability",
            )
        )

        return self.validate(entry)