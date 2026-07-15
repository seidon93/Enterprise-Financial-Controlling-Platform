"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : supplier_payment.py
Object Type     : Supplier Payment Scenario
Layer           : ETL
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from accounting.enums import DocumentType
from accounting.models import JournalEntry, JournalLine
from scenarios.base import AccountingScenario


@dataclass(slots=True, frozen=True)
class SupplierPaymentRequest:
    """
    Input data for supplier payment.
    """

    company_code: str
    cost_center_code: str
    department_code: str
    currency_code: str

    payment_date: date

    payment_amount: Decimal

    description: str = ""


class SupplierPaymentScenario(AccountingScenario):
    """
    Generates accounting entries for supplier payments.
    """

    def create(
        self,
        request: SupplierPaymentRequest,
    ) -> JournalEntry:

        document = self.document_generator.create(
            document_type=DocumentType.SP,
            posting_date=request.payment_date,
            document_date=request.payment_date,
            due_date=request.payment_date,
        )

        entry = JournalEntry(document=document)

        # Trade Payables
        entry.add_line(
            JournalLine(
                line_number=1,
                account_number="321",
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=request.payment_amount,
                credit_amount=Decimal("0.00"),
                amount_local=request.payment_amount,
                description="Supplier Payment",
            )
        )

        # Bank
        entry.add_line(
            JournalLine(
                line_number=2,
                account_number="221",
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=Decimal("0.00"),
                credit_amount=request.payment_amount,
                amount_local=request.payment_amount,
                description="Bank Payment",
            )
        )

        return self.validate(entry)