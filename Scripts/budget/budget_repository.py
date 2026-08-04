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


class BudgetRepository:
    """
    In-memory repository for budgets.
    """

    def __init__(self) -> None:

        self._budgets: list[Budget] = []

    def add(self, budget: Budget) -> None:

        self._budgets.append(budget)

    def get_all(self) -> list[Budget]:

        return list(self._budgets)