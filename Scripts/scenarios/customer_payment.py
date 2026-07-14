"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : customer_payment.py
Object Type     : Customer Payment Scenario
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
class CustomerPaymentRequest:
    """Input data for a customer payment."""

    company_code: str
    cost_center_code: str
    department_code: str
    currency_code: str

    invoice_date: date
    due_date: date

    net_amount: Decimal
    vat_rate: Decimal

    description: str = ""


class CustomerPaymentScenario(AccountingScenario):

    """Generates accounting entries for a customer payment."""

    def create(
        self,
        request: CustomerPaymentRequest,
    ) -> JournalEntry:

        vat_amount = (request.net_amount * request.vat_rate).quantize(
            Decimal("0.01")
        )

        gross_amount = request.net_amount + vat_amount

        document = self.document_generator.create(
            document_type=DocumentType.CP,
            posting_date=request.invoice_date,
            document_date=request.invoice_date,
            due_date=request.due_date,
        )

        entry = JournalEntry(document=document)

        # Bank
        entry.add_line(
            JournalLine(
                line_number=1,
                account_number="221",
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=gross_amount,
                credit_amount=Decimal("0.00"),
                amount_local=gross_amount,
                description="Customer Payment",
            )
        )

        # Trade Receivable
        entry.add_line(
            JournalLine(
                line_number=2,
                account_number="311",
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=Decimal("0.00"),
                credit_amount=gross_amount,
                amount_local=gross_amount,
                description="Trade Receivable Settlement",
            )
        )
        # VAT
#        entry.add_line(
#            JournalLine(
#                line_number=3,
#                account_number="343",
#                company_code=request.company_code,
#                cost_center_code=request.cost_center_code,
#                department_code=request.department_code,
#                currency_code=request.currency_code,
#                debit_amount=vat_amount,
#                credit_amount=Decimal("0.00"),
#                amount_local=vat_amount,
#                description="Input VAT",
#            )
#        )

        return self.validate(entry)