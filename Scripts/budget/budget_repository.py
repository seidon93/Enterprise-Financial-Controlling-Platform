"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : budget_repository.py
Object Type     : Budget Repository
Layer           : Budget
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Stores Budget objects in memory.
===============================================================================
"""

from __future__ import annotations


import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from Scripts.budget.budget import Budget
from Scripts.budget import budget_version
from Scripts import budget


class BudgetRepository:
    """
    In-memory repository for budgets.
    """

    def __init__(self) -> None:

        self._budgets: list[Budget] = []

    def add(self, budget: Budget) -> None:

        if self.exists(
            fiscal_year=budget.fiscal_year,
            version=budget.version,
        ):
            raise ValueError(
                "Budget already exists."
            )

        self._budgets.append(budget)

    def get_all(self) -> list[Budget]:

        return list(self._budgets)

    def get(
        self,
        *,
        fiscal_year: int,
        version,
    ):

        for budget in self._budgets:

            if (
                budget.fiscal_year == fiscal_year
                and budget.version == version
            ):
                return budget

        return None

    def exists(
        self,
        *,
        fiscal_year: int,
        version,
    ) -> bool:

        return (
            self.get(
                fiscal_year=fiscal_year,
                version=version,
            )
            is not None
        )

    def remove(
        self,
        *,
        fiscal_year: int,
        version,
    ) -> None:

        budget = self.get(
            fiscal_year=fiscal_year,
            version=version,
        )

        if budget is None:
            raise ValueError(
                "Budget does not exist."
            )

        self._budgets.remove(budget)

    def replace(
        self,
        budget: Budget,
    ) -> None:

        if self.exists(
            fiscal_year=budget.fiscal_year,
            version=budget.version,
        ):
            self.remove(
                fiscal_year=budget.fiscal_year,
                version=budget.version,
            )

        self._budgets.append(budget)

    def count(self) -> int:

        return len(self._budgets)

        