"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : sales_generator.py
Object Type     : Sales Generator
Layer           : Data Generation
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates realistic sales invoices and loads them into Fact_GL.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

_scripts_python = str(Path(__file__).resolve().parent.parent)      # Scripts/Python
_scripts_root  = str(Path(__file__).resolve().parent.parent.parent) # Scripts
sys.path.insert(0, _scripts_python)
sys.path.insert(0, _scripts_root)

import logging
from datetime import date
from decimal import Decimal

from accounting.loader import FactGLLoader
from scenarios.sales_invoice import (
    SalesInvoiceRequest,
    SalesInvoiceScenario,
)
from common.batch_context import BatchContext
from domain.business_data_provider import BusinessDataProvider

logger = logging.getLogger(__name__)


class SalesGenerator:
    """
    Generates sales invoices.
    """

    def __init__(
        self,
        provider: BusinessDataProvider,
        scenario: SalesInvoiceScenario,
        loader: FactGLLoader,
    ) -> None:

        self.provider = provider
        self.scenario = scenario
        self.loader = loader

    def generate(
        self,
        documents: int,
        batch: BatchContext,
    ) -> int:

        """
        Generate sales invoices.

        Returns number of inserted journal lines.
        """

        inserted = 0

        for _ in range(documents):

            company = self.provider.random_company()

            request = SalesInvoiceRequest(
                company_code=company.company_code,
                cost_center_code="1000",
                department_code="FIN",
                currency_code=company.currency_code,

                invoice_date=date.today(),
                due_date=date.today(),

                net_amount=Decimal("10000.00"),
                vat_rate=Decimal("0.21"),

                description="Generated Sales Invoice",
            )

            entry = self.scenario.create(request)

            inserted += self.loader.load(
                entry,
                batch,
            )

        logger.info(
            "Generated %s documents.",
            documents,
        )

        return inserted