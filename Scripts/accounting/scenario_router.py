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

from scenarios.purchase_invoice import (
    PurchaseInvoiceRequest,
    PurchaseInvoiceScenario,
)

from scenarios.customer_payment import (
    CustomerPaymentRequest,
    CustomerPaymentScenario,
)



class ScenarioRouter:
    """
    Converts BusinessEvents into JournalEntries.
    """

    def __init__(
        self,
        sales_scenario: SalesInvoiceScenario,
        purchase_scenario: PurchaseInvoiceScenario,
        customer_payment_scenario: CustomerPaymentScenario,
    ) -> None:

        self.sales_scenario = sales_scenario
        self.purchase_scenario = purchase_scenario
        self.customer_payment_scenario = customer_payment_scenario

    def process(
        self,
        event: BusinessEvent,
    ):

        match event.event_type:

            case BusinessEventType.SALES_INVOICE:

                request = SalesInvoiceRequest(
                    company_code=event.company_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    currency_code=event.currency_code,
                    invoice_date=event.event_date,
                    due_date=event.due_date,
                    net_amount=event.amount,
                    vat_rate=event.vat_rate,
                    description=event.description,
                )

                return self.sales_scenario.create(request)

            case BusinessEventType.PURCHASE_INVOICE:
                request = PurchaseInvoiceRequest(
                    company_code=event.company_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    currency_code=event.currency_code,
                    invoice_date=event.event_date,
                    due_date=event.due_date,
                    net_amount=event.amount,
                    vat_rate=event.vat_rate,
                    description=event.description,
                )
                return self.purchase_scenario.create(request)

            case BusinessEventType.CUSTOMER_PAYMENT:

                request = CustomerPaymentRequest(
                    company_code=event.company_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    currency_code=event.currency_code,
                    payment_date=event.event_date,
                    payment_amount=event.amount,
                    description=event.description,
                )

                return self.customer_payment_scenario.create(request)

            case _:

                raise NotImplementedError(
                    f"Unsupported event: {event.event_type}"
                )
    