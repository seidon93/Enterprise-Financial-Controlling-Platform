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
        Generate asset accounting documents.
        """

        inserted = 0

        for _ in range(documents):

            event = self.event_generator.asset_acquisition_event()

            journal = self.router.process(event)

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