"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : asset_generator.py
Object Type     : Asset Generator
Layer           : ETL Generation
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting entries for enterprise asset scenarios.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import logging
import random

# pyrefly: ignore [missing-import]
from common.batch_context import BatchContext

logger = logging.getLogger(__name__)


class AssetGenerator:
    """
    Generates accounting documents for asset transactions.
    """

    def __init__(
        self,
        provider,
        event_generator,
        router,
        loader,
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
        Generate enterprise asset accounting documents.
        """

        inserted = 0

        event_factories = [

            self.event_generator.asset_acquisition_event,
            self.event_generator.asset_capitalization_event,
            self.event_generator.asset_depreciation_event,
            self.event_generator.asset_impairment_event,
            self.event_generator.asset_disposal_event,
            self.event_generator.asset_sale_event,
            self.event_generator.asset_transfer_event,

        ]

        for _ in range(documents):

            event_factory = random.choice(
                event_factories
            )

            event = event_factory()

            journal = self.router.process(
                event
            )

            rows = self.loader.load(
                journal,
                batch.batch_id,
            )

            inserted += rows

        logger.info(
            "Generated %s asset accounting rows.",
            inserted,
        )

        return inserted