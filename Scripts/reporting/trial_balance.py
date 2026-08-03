"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : trial_balance.py
Object Type     : Financial Reporting Engine
Layer           : Reporting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Builds Trial Balance from General Ledger.
===============================================================================
"""

from __future__ import annotations

import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from accounting.models import JournalEntry


class TrialBalance:

    def __init__(self) -> None:

        self._accounts: dict[str, Decimal] = defaultdict(
            lambda: Decimal("0")
        )

    def add_entry(self, entry: JournalEntry) -> None:

        for line in entry.lines:

            self._accounts[line.account_number] += (
                line.debit_amount
                - line.credit_amount
            )

    @property
    def balances(self) -> dict[str, Decimal]:

        return dict(sorted(self._accounts.items()))

    @property
    def total_debit(self) -> Decimal:

        return sum(
            (
                amount
                for amount in self._accounts.values()
                if amount > 0
            ),
            Decimal("0"),
        )

    @property
    def total_credit(self) -> Decimal:

        return sum(
            (
                -amount
                for amount in self._accounts.values()
                if amount < 0
            ),
            Decimal("0"),
        )

    @property
    def is_balanced(self) -> bool:

        return self.total_debit == self.total_credit