"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : inventory_generator.py
Object Type     : Inventory Generator
Layer           : ETL Generation
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates enterprise inventory accounting scenarios.
===============================================================================
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import logging

# pyrefly: ignore [missing-import]
from common.batch_context import BatchContext
from domain.business_event_type import BusinessEventType

logger = logging.getLogger(__name__)


class InventoryGenerator:
    """
    Generates enterprise inventory transactions.
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

        inserted = 0

        scenario_weights = [

            (
                BusinessEventType.INVENTORY_RECEIPT,
                35,
            ),

            (
                BusinessEventType.INVENTORY_ISSUE,
                35,
            ),

            (
                BusinessEventType.INVENTORY_TRANSFER,
                15,
            ),

            (
                BusinessEventType.INVENTORY_ADJUSTMENT,
                15,
            ),

        ]

        events = [x[0] for x in scenario_weights]
        weights = [x[1] for x in scenario_weights]

        for _ in range(documents):

            event_type = random.choices(
                events,
                weights=weights,
                k=1,
            )[0]

            if event_type == BusinessEventType.INVENTORY_RECEIPT:

                event = self.event_generator.inventory_receipt_event()

            elif event_type == BusinessEventType.INVENTORY_ISSUE:

                event = self.event_generator.inventory_issue_event()

            elif event_type == BusinessEventType.INVENTORY_TRANSFER:

                event = self.event_generator.inventory_transfer_event()

            else:

                event = self.event_generator.inventory_adjustment_event()

            journal = self.router.process(event)

            rows = self.loader.load(
                journal,
                batch,
            )

            inserted += rows

        logger.info(
            "Generated %s inventory accounting rows.",
            inserted,
        )

        return inserted