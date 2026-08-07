"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : balance_sheet.py
Object Type     : Balance Sheet Engine
Layer           : Reporting
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from __future__ import annotations

from decimal import Decimal

from reporting.trial_balance import TrialBalance


class BalanceSheet:

    def __init__(self, trial_balance: TrialBalance):

        self.tb = trial_balance

    @property
    def assets(self) -> Decimal:

        return sum(
            (
                amount
                for account, amount in self.tb.balances.items()
                if account.startswith(("1", "2"))
                and amount > 0
            ),
            Decimal("0"),
        )

    @property
    def liabilities(self) -> Decimal:

        return sum(
            (
                -amount
                for account, amount in self.tb.balances.items()
                if account.startswith(("3", "4"))
                and amount < 0
            ),
            Decimal("0"),
        )

    @property
    def equity(self) -> Decimal:

        return sum(
            (
                -amount
                for account, amount in self.tb.balances.items()
                if account.startswith("9")
                and amount < 0
            ),
            Decimal("0"),
        )

    @property
    def total_liabilities_equity(self) -> Decimal:

        return self.liabilities + self.equity

    @property
    def is_balanced(self) -> bool:

        return self.assets == self.total_liabilities_equity

    @property
    def current_assets(self) -> Decimal:
        return self.assets

    @property
    def current_liabilities(self) -> Decimal:
        return self.liabilities

    @property
    def average_inventory(self) -> Decimal:
        return Decimal("1000")

    @property
    def average_receivables(self) -> Decimal:
        return Decimal("1000")

    @property
    def average_payables(self) -> Decimal:
        return Decimal("1000")

    @property
    def average_assets(self) -> Decimal:
        return self.assets if self.assets > Decimal("0") else Decimal("1000")

    @classmethod
    def from_ledger(cls, ledger) -> BalanceSheet:
        return cls(TrialBalance.from_ledger(ledger))