"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : scenario_engine.py
Object Type     : Scenario Engine
Layer           : ETL Orchestration
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Enterprise orchestration engine responsible for running accounting scenarios.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

_scripts_root   = str(Path(__file__).resolve().parent.parent)          # Scripts
_scripts_python = str(Path(__file__).resolve().parent.parent / "Python")  # Scripts/Python
sys.path.insert(0, _scripts_root)
sys.path.insert(0, _scripts_python)

import logging

from accounting.scenario_config import ScenarioConfig

from accounting.document_generator import DocumentGenerator
from accounting.dimension_mapper import DimensionMapper
from accounting.loader import FactGLLoader

from common.batch_context import BatchContext
from common.batch_logger import BatchLogger

from domain.business_data_provider import BusinessDataProvider
from domain.business_event_generator import BusinessEventGenerator

from accounting.scenario_router import ScenarioRouter
from scenarios.sales_invoice import SalesInvoiceScenario

from common.database import db

from Python.Generators.sales_generator import SalesGenerator

from scenarios.purchase_invoice import PurchaseInvoiceScenario
from Python.Generators.purchase_generator import PurchaseGenerator

from scenarios.customer_payment import CustomerPaymentScenario
from Python.Generators.customer_payment_generator import CustomerPaymentGenerator

from scenarios.supplier_payment import SupplierPaymentScenario
from Python.Generators.supplier_payment_generator import SupplierPaymentGenerator

from scenarios.assets.asset_acquisition import AssetAcquisitionScenario
from scenarios.assets.asset_capitalization import AssetCapitalizationScenario
from scenarios.assets.asset_depreciation import AssetDepreciationScenario
from scenarios.assets.asset_impairment import AssetImpairmentScenario
from scenarios.assets.asset_disposal import AssetDisposalScenario
from scenarios.assets.asset_sale import AssetSaleScenario
from scenarios.assets.asset_transfer import AssetTransferScenario
from Python.Generators.asset_generator import AssetGenerator

from accounting.load_mode import LoadMode

from Python.Generators.inventory_generator import InventoryGenerator

from scenarios.inventory.inventory_receipt import InventoryReceiptScenario
from scenarios.inventory.inventory_issue import InventoryIssueScenario
from scenarios.inventory.inventory_transfer import InventoryTransferScenario
from scenarios.inventory.inventory_adjustment import InventoryAdjustmentScenario

from Python.Generators.payroll_generator import PayrollGenerator

from scenarios.payroll.payroll_expense import PayrollExpenseScenario
from scenarios.payroll.employer_contribution import EmployerContributionScenario
from scenarios.payroll.payroll_tax import PayrollTaxScenario
from scenarios.payroll.payroll_payment import PayrollPaymentScenario

from scenarios.banking.bank_fee import BankFeeScenario
from scenarios.banking.interest_income import InterestIncomeScenario
from scenarios.banking.interest_expense import InterestExpenseScenario
from scenarios.banking.fx_gain import FXGainScenario
from scenarios.banking.fx_loss import FXLossScenario
from scenarios.banking.loan_drawdown import LoanDrawdownScenario
from scenarios.banking.loan_repayment import LoanRepaymentScenario
from scenarios.banking.cash_deposit import CashDepositScenario
from scenarios.banking.cash_withdrawal import CashWithdrawalScenario
from scenarios.banking.internal_transfer import InternalTransferScenario

from Python.Generators.bank_generator import BankGenerator

from scenarios.closing.accrued_expense import (
    AccruedExpenseScenario,
)

from Python.Generators.closing_generator import ClosingGenerator

logger = logging.getLogger(__name__)

print("Loaded ScenarioEngine from:")
print(__file__)

class ScenarioEngine:
    """
    Enterprise orchestration engine.
    """

    def __init__(self, config: ScenarioConfig) -> None:

        self.config = config

    def run_accounting(self) -> None:
        """
        Execute complete ETL generation.
        """

        logger.info("=" * 70)
        logger.info("Starting Enterprise Scenario Engine")
        logger.info("=" * 70)

        logger.info(
            "Period: %s - %s",
            self.config.start_year,
            self.config.end_year,
        )

        logger.info(
            "Companies: %s",
            ", ".join(self.config.companies),
        )

        logger.info(
            "Sales Documents: %s",
            f"{self.config.sales_documents:,}",
        )

        logger.info(
            "Vendor Documents: %s",
            f"{self.config.vendor_documents:,}",
        )

        logger.info(
            "Bank Transactions: %s",
            f"{self.config.bank_transactions:,}",
        )

        logger.info(
            "Inventory Transactions: %s",
            f"{self.config.inventory_transactions:,}",
        )

        logger.info(
            "Payroll Documents: %s",
            f"{self.config.payroll_documents:,}",
        )

        logger.info(
            "Asset Transactions: %s",
            f"{self.config.asset_transactions:,}",
        )

        logger.info(
            "Journal Entries: %s",
            f"{self.config.journal_entries:,}",
        )

        logger.info("=" * 70)

        logger.info("Scenario Engine initialized successfully.")

        match self.config.load_mode:

            case LoadMode.FULL:

                self.run_full()

            case LoadMode.SALES_ONLY:

                self.run_sales_only()

            case LoadMode.PURCHASE_ONLY:

                self.run_purchase_only()

            case LoadMode.CUSTOMER_PAYMENT_ONLY:

                self.run_customer_payment_only()

            case LoadMode.SUPPLIER_PAYMENT_ONLY:

                self.run_supplier_payment_only()

            case LoadMode.ASSET_ONLY:

                self.run_assets()

            case LoadMode.INVENTORY_ONLY:

                self.run_inventory()

            case LoadMode.PAYROLL_ONLY:

                self.run_payroll()

            case LoadMode.BANK_ONLY:

                self.run_banking()

            case LoadMode.CLOSING_ONLY:

                self.run_closing()

            case _:

                raise ValueError(
                    f"Unsupported load mode: {self.config.load_mode}"
                )



    def create_runtime(self):
        """
        Creates shared runtime objects used by all generators.
        """

        provider = BusinessDataProvider(
            seed=self.config.random_seed,
        )

        event_generator = BusinessEventGenerator(
            provider,
        )

        mapper = DimensionMapper(db)
        mapper.initialize()

        loader = FactGLLoader(
            db,
            mapper,
        )

        # ---------------------------------------------------------
        # ONE shared document generator for the whole ETL batch
        # ---------------------------------------------------------

        document_generator = DocumentGenerator()

        # ---------------------------------------------------------
        # Accounting scenarios
        # ---------------------------------------------------------

        sales_scenario = SalesInvoiceScenario(
            document_generator,
        )

        purchase_scenario = PurchaseInvoiceScenario(
            document_generator,
        )

        customer_payment_scenario = CustomerPaymentScenario(
            document_generator,
        )

        supplier_payment_scenario = SupplierPaymentScenario(
            document_generator,
        )

        asset_acquisition_scenario = AssetAcquisitionScenario(
            document_generator,
        )

        asset_capitalization_scenario = AssetCapitalizationScenario(
            document_generator,
        )

        asset_depreciation_scenario = AssetDepreciationScenario(
            document_generator,
        )

        asset_impairment_scenario = AssetImpairmentScenario(
            document_generator,
        )

        asset_disposal_scenario = AssetDisposalScenario(
            document_generator,
        )

        asset_sale_scenario = AssetSaleScenario(
            document_generator,
        )

        asset_transfer_scenario = AssetTransferScenario(
            document_generator,
        )

        inventory_receipt_scenario = InventoryReceiptScenario(
            document_generator,
        )

        inventory_issue_scenario = InventoryIssueScenario(
            document_generator,
        )

        inventory_transfer_scenario = InventoryTransferScenario(
            document_generator,
        )

        inventory_adjustment_scenario = InventoryAdjustmentScenario(
            document_generator,
        )

        payroll_expense_scenario = PayrollExpenseScenario(
            document_generator,
        )

        employer_contribution_scenario = EmployerContributionScenario(
            document_generator,
        )

        payroll_tax_scenario = PayrollTaxScenario(
            document_generator,
        )

        payroll_payment_scenario = PayrollPaymentScenario(
            document_generator,
        )

        bank_fee_scenario = BankFeeScenario(
            DocumentGenerator(),
        )

        interest_income_scenario = InterestIncomeScenario(
            DocumentGenerator(),
        )

        interest_expense_scenario = InterestExpenseScenario(
            DocumentGenerator(),
        )

        fx_gain_scenario = FXGainScenario(
            DocumentGenerator(),
        )

        fx_loss_scenario = FXLossScenario(
            DocumentGenerator(),
        )

        loan_drawdown_scenario = LoanDrawdownScenario(
            DocumentGenerator(),
        )

        loan_repayment_scenario = LoanRepaymentScenario(
            DocumentGenerator(),
        )

        cash_deposit_scenario = CashDepositScenario(
            DocumentGenerator(),
        )

        cash_withdrawal_scenario = CashWithdrawalScenario(
            DocumentGenerator(),
        )

        internal_transfer_scenario = InternalTransferScenario(
            DocumentGenerator(),
        )

        accrued_expense_scenario = AccruedExpenseScenario(
            document_generator,
        )
        
        # ---------------------------------------------------------
        # Router
        # ---------------------------------------------------------

        router = ScenarioRouter(
            sales_scenario=sales_scenario,
            purchase_scenario=purchase_scenario,
            customer_payment_scenario=customer_payment_scenario,
            supplier_payment_scenario=supplier_payment_scenario,
            asset_acquisition_scenario=asset_acquisition_scenario,
            asset_capitalization_scenario=asset_capitalization_scenario,
            asset_depreciation_scenario=asset_depreciation_scenario,
            asset_impairment_scenario=asset_impairment_scenario,
            asset_disposal_scenario=asset_disposal_scenario,
            asset_sale_scenario=asset_sale_scenario,
            asset_transfer_scenario=asset_transfer_scenario,
            inventory_receipt_scenario=inventory_receipt_scenario,
            inventory_issue_scenario=inventory_issue_scenario,
            inventory_transfer_scenario=inventory_transfer_scenario,
            inventory_adjustment_scenario=inventory_adjustment_scenario,
            payroll_expense_scenario=payroll_expense_scenario,
            employer_contribution_scenario=employer_contribution_scenario,
            payroll_tax_scenario=payroll_tax_scenario,
            payroll_payment_scenario=payroll_payment_scenario,
            bank_fee_scenario=bank_fee_scenario,
            interest_income_scenario=interest_income_scenario,
            interest_expense_scenario=interest_expense_scenario,
            fx_gain_scenario=fx_gain_scenario,
            fx_loss_scenario=fx_loss_scenario,
            loan_drawdown_scenario=loan_drawdown_scenario,
            loan_repayment_scenario=loan_repayment_scenario,
            cash_deposit_scenario=cash_deposit_scenario,
            cash_withdrawal_scenario=cash_withdrawal_scenario,
            internal_transfer_scenario=internal_transfer_scenario,
            accrued_expense_scenario=accrued_expense_scenario,
        )

        batch = BatchContext()

        return (
            provider,
            event_generator,
            loader,
            router,
            batch,
        )

    def run_full(self) -> None:
        """
        Execute complete accounting generation.
        """

        logger.info("=" * 70)
        logger.info("Generating Accounting Documents")
        logger.info("=" * 70)

        (
            provider,
            event_generator,
            loader,
            router,
            batch,
        ) = self.create_runtime()

        BatchLogger.start_batch(
            batch=batch,
            load_mode=self.config.load_mode.name,
        )

        sales_generator = SalesGenerator(
            provider,
            event_generator,
            router,
            loader,
        )

        purchase_generator = PurchaseGenerator(
            provider,
            event_generator,
            router,
            loader,
        )

        customer_payment_generator = CustomerPaymentGenerator(
            provider,
            event_generator,
            router,
            loader,
        )

        supplier_payment_generator = SupplierPaymentGenerator(
            provider,
            event_generator,
            router,
            loader,
        )
        inventory_generator = InventoryGenerator(
            provider,
            event_generator,
            router,
            loader,
        )

        payroll_generator = PayrollGenerator(
            provider,
            event_generator,
            router,
            loader,
        )

        asset_generator = AssetGenerator(
            provider,
            event_generator,
            router,
            loader,
        )


        bank_generator = BankGenerator(
            provider,
            event_generator,
            router,
            loader,
        )

        closing_generator = ClosingGenerator(
            provider,
            event_generator,
            router,
            loader,
        )

        sales_rows = sales_generator.generate(
            documents=self.config.sales_documents,
            batch=batch,
        )

        purchase_rows = purchase_generator.generate(
            documents=self.config.vendor_documents,
            batch=batch,
        )

        customer_payment_rows = customer_payment_generator.generate(
            documents=self.config.customer_payments,
            batch=batch,
        )

        supplier_payment_rows = supplier_payment_generator.generate(
            documents=self.config.supplier_payments,
            batch=batch,
        )

        asset_rows = asset_generator.generate(
            documents=self.config.asset_transactions,
            batch=batch,
        )

        inventory_rows = inventory_generator.generate(
            documents=self.config.inventory_transactions,
            batch=batch,
        )

        payroll_rows = payroll_generator.generate(
            documents=self.config.payroll_documents,
            batch=batch,
        )

        bank_rows = bank_generator.generate(
            documents=self.config.bank_transactions,
            batch=batch,
        )

        closing_rows = closing_generator.generate(
            documents=self.config.closing_documents,
            batch=batch,
        )

        inserted = (
            sales_rows
            + purchase_rows
            + customer_payment_rows
            + supplier_payment_rows
            + asset_rows
            + inventory_rows
            + payroll_rows
            + bank_rows
            + payroll_rows
        )


        BatchLogger.finish_batch(
            batch=batch,
            rows_inserted=inserted,
        )

        logger.info(
            "Sales rows inserted            : %s",
            sales_rows,
        )

        logger.info(
            "Purchase rows inserted         : %s",
            purchase_rows,
        )

        logger.info(
            "Customer payment rows inserted : %s",
            customer_payment_rows,
        )

        logger.info(
            "Supplier payment rows inserted : %s",
            supplier_payment_rows,
        )

        logger.info(
            "Asset rows inserted            : %s",
            asset_rows,
        )

        logger.info(
            "Total rows inserted            : %s",
            inserted,
        )

        logger.info(
            "Batch ID                       : %s",
            batch.batch_id,
        )

        logger.info(
            "Inventory rows inserted       : %s",
            inventory_rows,
        )

        logger.info(
            "Payroll rows inserted         : %s",
            payroll_rows,
        )

        logger.info(
            "Bank rows inserted            : %s",
            bank_rows,
        )

        logger.info(
            "Closing rows inserted         : %s",
            closing_rows,
        )



    def run_sales_only(self) -> None:
        """
        Generate only Sales Invoices.
        """

        logger.info("=" * 70)
        logger.info("Running SALES ONLY mode")
        logger.info("=" * 70)

        (
            provider,
            event_generator,
            loader,
            router,
            batch,
        ) = self.create_runtime()

        generator = SalesGenerator(
            provider,
            event_generator,
            router,
            loader,
        )

        inserted = generator.generate(
            documents=self.config.sales_documents,
            batch=batch,
        )

        logger.info(
            "Sales rows inserted: %s",
            inserted,
        )

        logger.info(
            "Batch ID: %s",
            batch.batch_id,
        )

    def run_purchase_only(self) -> None:
        """
        Generate only Purchase Invoices.
        """

        logger.info("=" * 70)
        logger.info("Running PURCHASE ONLY mode")
        logger.info("=" * 70)

        (
            provider,
            event_generator,
            loader,
            router,
            batch,
        ) = self.create_runtime()

        generator = PurchaseGenerator(
            provider,
            event_generator,
            router,
            loader,
        )

        inserted = generator.generate(
            documents=self.config.vendor_documents,
            batch=batch,
        )

        logger.info(
            "Purchase rows inserted: %s",
            inserted,
        )

        logger.info(
            "Batch ID: %s",
            batch.batch_id,
        )


    def run_customer_payment_only(self) -> None:
        """
        Generate only Customer Payments.
        """

        logger.info("=" * 70)
        logger.info("Running CUSTOMER PAYMENT ONLY mode")
        logger.info("=" * 70)

        (
            provider,
            event_generator,
            loader,
            router,
            batch,
        ) = self.create_runtime()

        generator = CustomerPaymentGenerator(
            provider,
            event_generator,
            router,
            loader,
        )

        inserted = generator.generate(
            documents=self.config.customer_payments,
            batch=batch,
        )

        logger.info(
            "Customer payment rows inserted: %s",
            inserted,
        )

        logger.info(
            "Batch ID: %s",
            batch.batch_id,
        )


    def run_supplier_payment_only(self) -> None:
        """
        Generate only Supplier Payments.
        """

        logger.info("=" * 70)
        logger.info("Running SUPPLIER PAYMENT ONLY mode")
        logger.info("=" * 70)

        (
            provider,
            event_generator,
            loader,
            router,
            batch,
        ) = self.create_runtime()

        supplier_payment_generator = SupplierPaymentGenerator(
            provider,
            event_generator,
            router,
            loader,
        )

        supplier_payment_rows = supplier_payment_generator.generate(
            documents=self.config.supplier_payments,
            batch=batch,
        )

        logger.info(
            "Supplier payment rows inserted : %s",
            supplier_payment_rows,
        )

        logger.info(
            "Batch ID : %s",
            batch.batch_id,
        )


    def run_assets(self) -> None:
        """
        Generate only Asset transactions.
        """

        logger.info("=" * 70)
        logger.info("Running ASSETS ONLY mode")
        logger.info("=" * 70)

        (
            provider,
            event_generator,
            loader,
            router,
            batch,
        ) = self.create_runtime()

        generator = AssetGenerator(
            provider,
            event_generator,
            router,
            loader,
        )

        inserted = generator.generate(
            documents=self.config.asset_transactions,
            batch=batch,
        )

        logger.info(
            "Asset rows inserted: %s",
            inserted,
        )

        logger.info(
            "Batch ID: %s",
            batch.batch_id,
        )
        
    def run_inventory(self) -> None:
        """
        Generate only Inventory transactions.
        """

        logger.info("=" * 70)
        logger.info("Running INVENTORY ONLY mode")
        logger.info("=" * 70)

        (
            provider,
            event_generator,
            loader,
            router,
            batch,
        ) = self.create_runtime()

        generator = InventoryGenerator(
            provider,
            event_generator,
            router,
            loader,
        )

        inserted = generator.generate(
            documents=self.config.inventory_transactions,
            batch=batch,
        )

        logger.info(
            "Inventory rows inserted: %s",
            inserted,
        )

        logger.info(
            "Batch ID: %s",
            batch.batch_id,
        )


    def run_payroll(self) -> None:
        """
        Generate only Payroll transactions.
        """

        logger.info("=" * 70)
        logger.info("Running PAYROLL ONLY mode")
        logger.info("=" * 70)

        (
            provider,
            event_generator,
            loader,
            router,
            batch,
        ) = self.create_runtime()

        generator = PayrollGenerator(
            provider,
            event_generator,
            router,
            loader,
        )

        inserted = generator.generate(
            documents=self.config.payroll_documents,
            batch=batch,
        )

        logger.info(
            "Payroll rows inserted: %s",
            inserted,
        )

        logger.info(
            "Batch ID: %s",
            batch.batch_id,
        )

    def run_banking(self) -> None:
        """
        Generate only Banking & Treasury transactions.
        """

        logger.info("=" * 70)
        logger.info("Running BANKING ONLY mode")
        logger.info("=" * 70)

        (
            provider,
            event_generator,
            loader,
            router,
            batch,
        ) = self.create_runtime()

        generator = BankGenerator(
            provider,
            event_generator,
            router,
            loader,
        )

        inserted = generator.generate(
            documents=self.config.bank_transactions,
            batch=batch,
        )

        logger.info(
            "Banking rows inserted: %s",
            inserted,
        )

        logger.info(
            "Batch ID: %s",
            batch.batch_id,
        )

    def run_vendor(self) -> None:
        logger.info("Vendor scenario not implemented yet.")



  