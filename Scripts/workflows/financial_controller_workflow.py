"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : financial_controller_workflow.py
Object Type     : Financial Controller Workflow
Layer           : Application
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

from accounting.document_generator import DocumentGenerator
from accounting.general_ledger_engine import GeneralLedgerEngine

from repositories.journal_repository import JournalRepository

from scenarios.sales_invoice import (
    SalesInvoiceRequest,
    SalesInvoiceScenario,
)

from scenarios.purchase_invoice import (
    PurchaseInvoiceRequest,
    PurchaseInvoiceScenario,
)

from services.financial_controller_service import (
    FinancialControllerService,
)


class FinancialControllerWorkflow:
    """
    Orchestrates the end-to-end financial controller workflow.
    """

    def __init__(
        self,
        journal_repository: JournalRepository,
        document_generator: DocumentGenerator,
    ) -> None:

        self.journal_repository = journal_repository

        self.sales_invoice_scenario = SalesInvoiceScenario(
            document_generator
        )

        self.purchase_invoice_scenario = PurchaseInvoiceScenario(
            document_generator
        )

    def generate_transactions(self) -> None:

        sales_invoice = self.sales_invoice_scenario.create(
            SalesInvoiceRequest(
                company_code="1000",
                cost_center_code="100",
                department_code="D01",
                currency_code="CZK",
                invoice_date=date(2026, 1, 15),
                due_date=date(2026, 2, 15),
                net_amount=Decimal("50000"),
                vat_rate=Decimal("0.21"),
                description="Sales invoice",
                customer_code="CUST-001",
            )
        )

        purchase_invoice = self.purchase_invoice_scenario.create(
            PurchaseInvoiceRequest(
                company_code="1000",
                cost_center_code="100",
                department_code="D01",
                currency_code="CZK",
                supplier_code="SUP-001",
                invoice_date=date(2026, 1, 15),
                due_date=date(2026, 2, 15),
                net_amount=Decimal("20000"),
                vat_rate=Decimal("0.21"),
                description="Purchase invoice",
            )
        )

        self.journal_repository.save(
            sales_invoice
        )

        self.journal_repository.save(
            purchase_invoice
        )

    def build_general_ledger(
        self,
    ) -> GeneralLedgerEngine:

        ledger = GeneralLedgerEngine()

        for entry in self.journal_repository.get_all():
            ledger.post(entry)

        return ledger

    def create_report(self):

        ledger = self.build_general_ledger()

        return FinancialControllerService.create_report(
            ledger
        )

    def run(self):

        self.generate_transactions()

        return self.create_report()


def run_financial_controller_workflow():

    document_generator = DocumentGenerator()

    journal_repository = JournalRepository()

    workflow = FinancialControllerWorkflow(
        journal_repository=journal_repository,
        document_generator=document_generator,
    )

    return workflow.run()