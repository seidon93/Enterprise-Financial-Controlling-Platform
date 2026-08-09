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
class SalesInvoiceRequest:
    """Input data for a sales invoice."""

    company_code: str
    cost_center_code: str
    department_code: str
    currency_code: str

    invoice_date: date
    due_date: date

    net_amount: Decimal
    vat_rate: Decimal

    description: str = ""

    customer_code: str | None = None

    product_code: str | None = None
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    material_code: str | None = None


class SalesInvoiceScenario(AccountingScenario):
    """
    Generates accounting entries for a sales invoice.
    """

    def create(
        self,
        request: SalesInvoiceRequest,
    ) -> JournalEntry:

        vat_amount = (request.net_amount * request.vat_rate).quantize(
            Decimal("0.01")
        )

        gross_amount = request.net_amount + vat_amount

        document = self.document_generator.create(
            document_type=DocumentType.AR,
            posting_date=request.invoice_date,
            document_date=request.invoice_date,
            due_date=request.due_date,
        )

        entry = JournalEntry(document=document)

        # Receivable
        entry.add_line(
            JournalLine(
                line_number=1,
                account_number="211",
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=gross_amount,
                credit_amount=Decimal("0.00"),
                amount_local=gross_amount,
                description="Customer Receivable",
                customer_code=request.customer_code,
                product_code=request.product_code,
                quantity=request.quantity,
                unit_price=request.unit_price,
                material_code=request.material_code,
                
            )
        )

        # Revenue
        entry.add_line(
            JournalLine(
                line_number=2,
                account_number="602",
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=Decimal("0.00"),
                credit_amount=request.net_amount,
                amount_local=request.net_amount,
                description="Sales Revenue",
                customer_code=request.customer_code,
                product_code=request.product_code,
                quantity=request.quantity,
                unit_price=request.unit_price,
                material_code=request.material_code,
            )
        )

        # VAT
        entry.add_line(
            JournalLine(
                line_number=3,
                account_number="432",
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=Decimal("0.00"),
                credit_amount=vat_amount,
                amount_local=vat_amount,
                description="Output VAT",
                customer_code=request.customer_code,
            )
        )

        return self.validate(entry)