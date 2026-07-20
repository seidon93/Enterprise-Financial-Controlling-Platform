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
from decimal import Decimal

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
            cost_center_code=transaction.cost_center_code,
            department_code=transaction.department_code,
            vat_rate=transaction.vat_rate,
            due_date=transaction.due_date,
            customer_code=transaction.customer_code,
        )

    def purchase_event(self) -> BusinessEvent:
        """
        Generate one purchase business event.
        """

        transaction = self.provider.create_purchase_transaction()

        return BusinessEvent(
            event_type=BusinessEventType.PURCHASE_INVOICE,
            company_code=transaction.company_code,
            event_date=transaction.invoice_date,
            amount=transaction.amount,
            currency_code=transaction.currency_code,
            description=transaction.description,
            cost_center_code=transaction.cost_center_code,
            department_code=transaction.department_code,
            vat_rate=transaction.vat_rate,
            due_date=transaction.due_date,
            customer_code=None,
            supplier_code=transaction.supplier_code,
        )

    def customer_payment_event(self) -> BusinessEvent:
        """
        Generate one customer payment business event.
        """

        transaction = self.provider.create_customer_payment_transaction()

        return BusinessEvent(
            event_type=BusinessEventType.CUSTOMER_PAYMENT,
            company_code=transaction.company_code,
            event_date=transaction.invoice_date,
            amount=transaction.amount,
            currency_code=transaction.currency_code,
            description=transaction.description,
            cost_center_code=transaction.cost_center_code,
            department_code=transaction.department_code,
            vat_rate=transaction.vat_rate,
            due_date=transaction.due_date,
            customer_code=transaction.customer_code,
        )

  

    def supplier_payment_event(self) -> BusinessEvent:
        """
        Generate one supplier payment business event.
        """

        transaction = self.provider.create_supplier_payment_transaction()

        return BusinessEvent(
            event_type=BusinessEventType.SUPPLIER_PAYMENT,
            company_code=transaction.company_code,
            event_date=transaction.invoice_date,
            amount=transaction.amount,
            currency_code=transaction.currency_code,
            description=transaction.description,
            cost_center_code=transaction.cost_center_code,
            department_code=transaction.department_code,
            vat_rate=transaction.vat_rate,
            due_date=transaction.due_date,
            customer_code=None,
            supplier_code=transaction.supplier_code,
            
        )