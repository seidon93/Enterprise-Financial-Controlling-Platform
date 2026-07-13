"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : business_event_generator.py
Object Type     : Business Event Generator
Layer           : Domain
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domain.business_event import BusinessEvent
from domain.business_event_type import BusinessEventType
from domain.business_data_provider import BusinessDataProvider


class BusinessEventGenerator:
    """
    Generates business events from business transactions.
    """

    def __init__(
        self,
        provider: BusinessDataProvider,
    ) -> None:

        self.provider = provider

    def sales_event(self) -> BusinessEvent:
        """
        Generate one sales business event.
        """

        transaction = self.provider.create_sales_transaction()

        return BusinessEvent(
            event_type=BusinessEventType.SALES_INVOICE,
            company_code=transaction.company_code,
            event_date=transaction.invoice_date,
            amount=transaction.amount,
            currency_code=transaction.currency_code,
            description=transaction.description,
        )