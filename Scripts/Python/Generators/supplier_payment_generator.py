"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : supplier_payment_generator.py
Object Type     : Supplier Payment Generator
Layer           : Data Generation
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates realistic supplier payments and loads them into Fact_GL.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

_scripts_python = str(Path(__file__).resolve().parent.parent)
_scripts_root = str(Path(__file__).resolve().parent.parent.parent)

sys.path.insert(0, _scripts_python)
sys.path.insert(0, _scripts_root)

import logging

from accounting.loader import FactGLLoader

# pyrefly: ignore [missing-import]
from common.batch_context import BatchContext

from domain.business_data_provider import BusinessDataProvider
from domain.business_event_generator import BusinessEventGenerator

from accounting.scenario_router import ScenarioRouter

logger = logging.getLogger(__name__)


class SupplierPaymentGenerator:
    """
    Generates supplier payments.
    """

    def __init__(
        self,
        provider: BusinessDataProvider,
        event_generator: BusinessEventGenerator,
        router: ScenarioRouter,
        loader: FactGLLoader,
    ) -> None:

        self.provider = provider
        self.event_generator = event_generator
        self.router = router
        self.loader = loader

    def generate(
        self,
        documents: int,
        batch: BatchContext,
    ) -> int:
        """
        Generate supplier payments.

        Returns
        -------
        int
            Number of inserted journal lines.
        """

        inserted = 0

        for _ in range(documents):

            event = self.event_generator.supplier_payment_event()

            entry = self.router.process(event)

            inserted += self.loader.load(
                entry,
                batch,
            )

        logger.info(
            "Generated %s supplier payments.",
            documents,
        )

        return inserted