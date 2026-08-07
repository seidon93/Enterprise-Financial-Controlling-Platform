"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : income_statement.py
Object Type     : Income Statement Engine
Layer           : Reporting
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from __future__ import annotations

from decimal import Decimal
from reporting.trial_balance import TrialBalance


class IncomeStatement:
    """
    Profit & Loss Statement.
    """

    def __init__(self, trial_balance: TrialBalance):

        self.tb = trial_balance

    @property
    def revenues(self) -> Decimal:

        return sum(
            (
                -amount
                for account, amount in self.tb.balances.items()
                if account.startswith("6")
                and amount < 0
            ),
            Decimal("0"),
        )

    @property
    def expenses(self) -> Decimal:

        return sum(
            (
                amount
                for account, amount in self.tb.balances.items()
                if account.startswith("5")
                and amount > 0
            ),
            Decimal("0"),
        )

    @property
    def operating_profit(self) -> Decimal:

        return self.revenues - self.expenses

    @property
    def net_profit(self) -> Decimal:

        return self.operating_profit

    @classmethod
    def from_ledger(cls, ledger) -> IncomeStatement:
        return cls(TrialBalance.from_ledger(ledger))