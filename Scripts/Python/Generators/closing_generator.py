"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : closing_generator.py
Object Type     : Closing Generator
Layer           : ETL Generation
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates Closing & General Ledger accounting events.
===============================================================================
"""

from __future__ import annotations

import logging
import random

# pyrefly: ignore [missing-import]
from common.batch_context import BatchContext


logger = logging.getLogger(__name__)


class ClosingGenerator:
    """
    Generates Closing accounting events.
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
        Generate Closing journal entries.
        """

        logger.info("=" * 70)
        logger.info("Generating Closing Transactions")
        logger.info("=" * 70)

        inserted_rows = 0

        summary: dict[str, int] = {}

        event_builders = [

            self.event_generator.accrued_expense_event,
            self.event_generator.accrued_revenue_event,
            self.event_generator.prepaid_expense_event,
            self.event_generator.deferred_revenue_event,
            self.event_generator.provision_event,
            self.event_generator.inventory_writeoff_event,
            self.event_generator.inventory_revaluation_event,
        ]

        for _ in range(documents):

            event = random.choice(
                event_builders
            )()

            journal = self.router.process(
                event
            )

            rows = self.loader.load(
                journal,
                batch=batch,
            )

            inserted_rows += rows

            summary[event.event_type.name] = (
                summary.get(
                    event.event_type.name,
                    0,
                )
                + 1
            )

        logger.info("=" * 70)
        logger.info("CLOSING SUMMARY")
        logger.info("=" * 70)

        for name, count in sorted(summary.items()):

            logger.info(
                "%-35s %10d",
                name,
                count,
            )

        logger.info("=" * 70)

        return inserted_rows