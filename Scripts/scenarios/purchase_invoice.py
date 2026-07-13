"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : sales_invoice.py
Object Type     : Sales Invoice Scenario
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
class PurchaseInvoiceRequest:
    """Input data for a purchase invoice."""

    company_code: str
    cost_center_code: str
    department_code: str
    currency_code: str

    invoice_date: date
    due_date: date

    net_amount: Decimal
    vat_rate: Decimal

    description: str = ""


class PurchaseInvoiceScenario(AccountingScenario):

    """Generates accounting entries for a purchase invoice."""

    def create(
        self,
        request: PurchaseInvoiceRequest,
    ) -> JournalEntry:

        vat_amount = (request.net_amount * request.vat_rate).quantize(
            Decimal("0.01")
        )

        gross_amount = request.net_amount + vat_amount

        document = self.document_generator.create(
            document_type=DocumentType.AP,
            posting_date=request.invoice_date,
            document_date=request.invoice_date,
            due_date=request.due_date,
        )

        entry = JournalEntry(document=document)

        # Payable
        entry.add_line(
            JournalLine(
                line_number=1,
                account_number="321",
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=Decimal("0.00"),
                credit_amount=gross_amount,
                amount_local=gross_amount,
                description="Vendor Payable",
            )
        )

        # Revenue
        entry.add_line(
            JournalLine(
                line_number=2,
                account_number="504",
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=request.net_amount,
                credit_amount=Decimal("0.00"),
                amount_local=request.net_amount,
                description="Material Purchase",
            )
        )

        # VAT
        entry.add_line(
            JournalLine(
                line_number=3,
                account_number="343",
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=vat_amount,
                credit_amount=Decimal("0.00"),
                amount_local=vat_amount,
                description="Input VAT",
            )
        )

        return self.validate(entry)