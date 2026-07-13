"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : scenario_router.py
Object Type     : Scenario Router
Layer           : Accounting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Routes business events to accounting scenarios.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domain.business_event import BusinessEvent
from domain.business_event_type import BusinessEventType

from decimal import Decimal

from scenarios.sales_invoice import (
    SalesInvoiceRequest,
    SalesInvoiceScenario,
)


class ScenarioRouter:
    """
    Converts BusinessEvents into JournalEntries.
    """

    def __init__(
        self,
        sales_scenario: SalesInvoiceScenario,
    ) -> None:

        self.sales_scenario = sales_scenario

    def process(
        self,
        event: BusinessEvent,
    ):

        match event.event_type:

            case BusinessEventType.SALES_INVOICE:

                request = SalesInvoiceRequest(
                    company_code=event.company_code,
                    cost_center_code="1000",
                    department_code="SAL",
                    currency_code=event.currency_code,
                    invoice_date=event.event_date,
                    due_date=event.event_date,
                    net_amount=event.amount,
                    vat_rate=Decimal("0.21"),
                    description=event.description,
                )

                return self.sales_scenario.create(request)

            case _:

                raise NotImplementedError(
                    f"Unsupported event: {event.event_type}"
                )