"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : payroll_generator.py
Object Type     : Payroll Generator
Layer           : ETL
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from __future__ import annotations

from random import choice


# pyrefly: ignore [missing-import]
from common.batch_context import BatchContext
from domain.business_event_type import BusinessEventType


class PayrollGenerator:

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

        rows = 0

        for _ in range(documents):

            event_type = choice(
                [
                    BusinessEventType.PAYROLL_EXPENSE,
                    BusinessEventType.EMPLOYER_CONTRIBUTION,
                    BusinessEventType.PAYROLL_TAX,
                    BusinessEventType.PAYROLL_PAYMENT,
                ]
            )

            match event_type:

                case BusinessEventType.PAYROLL_EXPENSE:
                    event = self.event_generator.payroll_expense_event()

                case BusinessEventType.EMPLOYER_CONTRIBUTION:
                    event = self.event_generator.employer_contribution_event()

                case BusinessEventType.PAYROLL_TAX:
                    event = self.event_generator.payroll_tax_event()

                case BusinessEventType.PAYROLL_PAYMENT:
                    event = self.event_generator.payroll_payment_event()

            journal = self.router.process(event)

            rows += self.loader.load(
                journal,
                batch,
            )

        return rows