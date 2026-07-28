"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : payroll_payment.py
Object Type     : Payroll Payment Scenario
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting entries for payroll payment.
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
class PayrollPaymentRequest:
    """
    Input data for payroll payment.
    """

    company_code: str

    employee_code: str

    payment_date: date

    payment_amount: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str


class PayrollPaymentScenario(AccountingScenario):
    """
    Generates payroll payment journal entry.
    """

    def create(
        self,
        request: PayrollPaymentRequest,
    ) -> JournalEntry:

        document = self.document_generator.create(
            document_type=DocumentType.PAYROLL,
            posting_date=request.payment_date,
            document_date=request.payment_date,
            due_date=request.payment_date,
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
                debit_amount=request.payment_amount,
                credit_amount=Decimal("0.00"),
                amount_local=request.payment_amount,
                description="Payroll Payment",
            )
        )

        # DAL 221
        entry.add_line(
            JournalLine(
                line_number=2,
                account_number=PayrollAccounts.BANK,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                employee_code=request.employee_code,
                debit_amount=Decimal("0.00"),
                credit_amount=request.payment_amount,
                amount_local=request.payment_amount,
                description="Bank Payment",
            )
        )

        return self.validate(entry)