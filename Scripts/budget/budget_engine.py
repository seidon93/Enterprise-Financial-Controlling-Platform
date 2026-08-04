from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from Scripts.budget.budget_line import BudgetLine


class BudgetEngine:
    """
    Enterprise Budget Engine.

    Provides budget aggregation utilities.
    """

    @staticmethod
    def total_budget(
        budget_lines: list[BudgetLine],
    ) -> Decimal:

        return sum(
            (line.amount for line in budget_lines),
            start=Decimal("0"),
        )