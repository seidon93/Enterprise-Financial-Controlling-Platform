"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : bank_generator.py
Object Type     : Banking Generator
Layer           : Data Generation
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates Banking & Treasury accounting transactions.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import random

from domain.business_event_type import BusinessEventType



class BankGenerator:
    """
    Generates Banking & Treasury transactions.
    """

    EVENT_TYPES = [
        (BusinessEventType.BANK_FEE, 10),
        (BusinessEventType.INTEREST_INCOME, 5),
        (BusinessEventType.INTEREST_EXPENSE, 8),
        (BusinessEventType.FX_GAIN, 7),
        (BusinessEventType.FX_LOSS, 7),
        (BusinessEventType.LOAN_DRAWDOWN, 3),
        (BusinessEventType.LOAN_REPAYMENT, 6),
        (BusinessEventType.CASH_DEPOSIT, 12),
        (BusinessEventType.CASH_WITHDRAWAL, 12),
        (BusinessEventType.INTERNAL_TRANSFER, 30),
    ]

    def __init__(
        self,
        provider,
        event_generator,
        router,
        loader,
    ):

        self.provider = provider
        self.event_generator = event_generator
        self.router = router
        self.loader = loader

        self.random = random.Random()

        self.event_map = {
            BusinessEventType.BANK_FEE:
                self.event_generator.bank_fee_event,

            BusinessEventType.INTEREST_INCOME:
                self.event_generator.interest_income_event,

            BusinessEventType.INTEREST_EXPENSE:
                self.event_generator.interest_expense_event,

            BusinessEventType.FX_GAIN:
                self.event_generator.fx_gain_event,

            BusinessEventType.FX_LOSS:
                self.event_generator.fx_loss_event,

            BusinessEventType.LOAN_DRAWDOWN:
                self.event_generator.loan_drawdown_event,

            BusinessEventType.LOAN_REPAYMENT:
                self.event_generator.loan_repayment_event,

            BusinessEventType.CASH_DEPOSIT:
                self.event_generator.cash_deposit_event,

            BusinessEventType.CASH_WITHDRAWAL:
                self.event_generator.cash_withdrawal_event,

            BusinessEventType.INTERNAL_TRANSFER:
                self.event_generator.internal_transfer_event,
        }

    def generate(
        self,
        documents: int,
        batch,
    ) -> int:
        """
        Generates banking documents.
        """

        inserted_rows = 0

        statistics = {
            event_type: 0
            for event_type, _ in self.EVENT_TYPES
        }

        population = [
            event_type
            for event_type, _ in self.EVENT_TYPES
        ]

        weights = [
            weight
            for _, weight in self.EVENT_TYPES
        ]

        for _ in range(documents):

            event_type = self.random.choices(
                population=population,
                weights=weights,
                k=1,
            )[0]

            event = self.event_map[event_type]()

            journal = self.router.process(event)

            inserted_rows += self.loader.load(
                journal,
                batch,
            )

            statistics[event_type] += 1

        print()

        print("=" * 70)
        print("BANKING SUMMARY")
        print("=" * 70)

        for event_type, count in statistics.items():

            print(
                f"{event_type.value:<30} {count:>10}"
            )

        print("=" * 70)

        return inserted_rows