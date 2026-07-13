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
from scenarios.sales_invoice import SalesInvoiceScenario

from common.batch_context import BatchContext
from common.database import db

from domain.business_data_provider import BusinessDataProvider
from domain.business_event_generator import BusinessEventGenerator
from accounting.scenario_router import ScenarioRouter
from Python.Generators.sales_generator import SalesGenerator

from scenarios.purchase_invoice import PurchaseInvoiceScenario
from Python.Generators.purchase_generator import PurchaseGenerator


logger = logging.getLogger(__name__)


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

        self.run_accounting()

    # -------------------------------------------------------------------------
    # Future scenario methods
    # -------------------------------------------------------------------------

    def run_sales(self) -> None:
        """
        Execute Sales and Purchase Invoice generation.
        """

        logger.info("=" * 70)
        logger.info("Generating Accounting Documents")
        logger.info("=" * 70)

        provider = BusinessDataProvider(
            seed=self.config.random_seed
        )

        event_generator = BusinessEventGenerator(
            provider
        )

        mapper = DimensionMapper(db)
        mapper.initialize()

        loader = FactGLLoader(
            db,
            mapper,
        )

        sales_scenario = SalesInvoiceScenario(
            DocumentGenerator()
        )

        purchase_scenario = PurchaseInvoiceScenario(
            DocumentGenerator()
        )

        router = ScenarioRouter(
            sales_scenario=sales_scenario,
            purchase_scenario=purchase_scenario,
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

        batch = BatchContext()

        sales_rows = sales_generator.generate(
            documents=self.config.sales_documents,
            batch=batch,
        )

        purchase_rows = purchase_generator.generate(
            documents=self.config.vendor_documents,
            batch=batch,
        )

        inserted = sales_rows + purchase_rows

        logger.info(
            "Sales rows inserted     : %s",
            sales_rows,
        )

        logger.info(
            "Purchase rows inserted : %s",
            purchase_rows,
        )

        logger.info(
            "Total rows inserted    : %s",
            inserted,
        )

        logger.info(
            "Batch ID               : %s",
            batch.batch_id,
        )

    def run_vendor(self) -> None:
        logger.info("Vendor scenario not implemented yet.")

    def run_bank(self) -> None:
        logger.info("Bank scenario not implemented yet.")

    def run_inventory(self) -> None:
        logger.info("Inventory scenario not implemented yet.")

    def run_payroll(self) -> None:
        logger.info("Payroll scenario not implemented yet.")

    def run_assets(self) -> None:
        logger.info("Assets scenario not implemented yet.")