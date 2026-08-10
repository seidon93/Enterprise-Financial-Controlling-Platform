"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : financial_controller_workflow.py
Object Type     : Workflow
Layer           : Application / Workflow Layer
Version         : 3.0.0
Status          : Development

Description:
    Orchestrates the end-to-end Financial Controller workflow.

    The workflow generates comparable sales transactions for two fiscal
    periods (previous year and current year) so that controller analytics
    such as Price × Volume can be calculated from actual transaction data.

Flow:

    Sales / Purchase Transactions
            ↓
    JournalRepository
            ↓
    GeneralLedgerEngine
            ↓
    FinancialControllerService
            ↓
    FinancialControllerReport
===============================================================================
"""

from datetime import date
from decimal import Decimal

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
    Orchestrates the end-to-end Financial Controller workflow.
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
        """
        Generate controller demonstration transactions.

        Two comparable sales periods are generated:

        Previous year:
            2025
            Quantity: 485
            Unit price: 95 CZK
            Revenue: 46,075 CZK

        Current year:
            2026
            Quantity: 500
            Unit price: 100 CZK
            Revenue: 50,000 CZK

        These transactions provide the actual data required for
        Price × Volume analysis.
        """

        # ------------------------------------------------------------------
        # PREVIOUS YEAR SALES
        # ------------------------------------------------------------------

        previous_year_sales = (
            self.sales_invoice_scenario.create(
                SalesInvoiceRequest(
                    company_code="1000",
                    cost_center_code="100",
                    department_code="D01",
                    currency_code="CZK",

                    invoice_date=date(2025, 1, 15),
                    due_date=date(2025, 2, 15),

                    net_amount=Decimal("46075.00"),
                    vat_rate=Decimal("0.21"),

                    description="Sales invoice - previous year",

                    customer_code="CUST-001",

                    material_code="MAT-001",
                    quantity=Decimal("485"),
                    unit_price=Decimal("95.00"),
                )
            )
        )

        # ------------------------------------------------------------------
        # CURRENT YEAR SALES
        # ------------------------------------------------------------------

        current_year_sales = (
            self.sales_invoice_scenario.create(
                SalesInvoiceRequest(
                    company_code="1000",
                    cost_center_code="100",
                    department_code="D01",
                    currency_code="CZK",

                    invoice_date=date(2026, 1, 15),
                    due_date=date(2026, 2, 15),

                    net_amount=Decimal("50000.00"),
                    vat_rate=Decimal("0.21"),

                    description="Sales invoice - current year",

                    customer_code="CUST-001",

                    material_code="MAT-001",
                    quantity=Decimal("500"),
                    unit_price=Decimal("100.00"),
                )
            )
        )

        # ------------------------------------------------------------------
        # CURRENT YEAR PURCHASE
        # ------------------------------------------------------------------

        purchase_invoice = (
            self.purchase_invoice_scenario.create(
                PurchaseInvoiceRequest(
                    company_code="1000",
                    cost_center_code="100",
                    department_code="D01",
                    currency_code="CZK",

                    supplier_code="SUP-001",

                    invoice_date=date(2026, 1, 15),
                    due_date=date(2026, 2, 15),

                    net_amount=Decimal("20000.00"),
                    vat_rate=Decimal("0.21"),

                    description="Purchase invoice",
                )
            )
        )

        # ------------------------------------------------------------------
        # PERSIST JOURNAL ENTRIES
        # ------------------------------------------------------------------

        self.journal_repository.save(
            previous_year_sales
        )

        self.journal_repository.save(
            current_year_sales
        )

        self.journal_repository.save(
            purchase_invoice
        )

    def build_general_ledger(
        self,
    ) -> GeneralLedgerEngine:
        """
        Build General Ledger from all journal entries.
        """

        ledger = GeneralLedgerEngine()

        for entry in self.journal_repository.get_all():
            ledger.post(entry)

        return ledger

    def create_report(self):
        """
        Create Financial Controller report from General Ledger.
        """

        ledger = self.build_general_ledger()

        return FinancialControllerService.create_report(
            ledger
        )

    def run(self):
        """
        Execute complete Financial Controller workflow.
        """

        self.generate_transactions()

        return self.create_report()


def run_financial_controller_workflow():
    """
    Application entry point for the Financial Controller workflow.
    """

    document_generator = DocumentGenerator()

    journal_repository = JournalRepository()

    workflow = FinancialControllerWorkflow(
        journal_repository=journal_repository,
        document_generator=document_generator,
    )

    return workflow.run()


if __name__ == "__main__":
    run_financial_controller_workflow()

