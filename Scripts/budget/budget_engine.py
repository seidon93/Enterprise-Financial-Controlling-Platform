from __future__ import annotations

import sys
from collections import defaultdict
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

    @staticmethod
    def budget_by_account(
        budget_lines: list[BudgetLine],
    ) -> dict[str, Decimal]:

        result = defaultdict(lambda: Decimal("0"))

        for line in budget_lines:
            result[line.account_number] += line.amount

        return dict(result)

    @staticmethod
    def budget_by_cost_center(
        budget_lines: list[BudgetLine],
    ):

        result = defaultdict(lambda: Decimal("0"))

        for line in budget_lines:
            result[line.cost_center_code] += line.amount

        return dict(result)

    @staticmethod
    def budget_by_company(
        budget_lines: list[BudgetLine],
    ):

        result = defaultdict(lambda: Decimal("0"))

        for line in budget_lines:
            result[line.company_code] += line.amount

        return dict(result)

    @staticmethod
    def budget_by_account(
        budget_lines: list[BudgetLine],
    ) -> dict[str, Decimal]:

        result = defaultdict(lambda: Decimal("0"))

        for line in budget_lines:
            result[line.account_code] += line.amount

        return dict(result)

    @staticmethod
    def budget_by_cost_center(
        budget_lines: list[BudgetLine],
    ):

        result = defaultdict(lambda: Decimal("0"))

        for line in budget_lines:
            result[line.cost_center_code] += line.amount

        return dict(result)

    @staticmethod
    def budget_by_company(
        budget_lines: list[BudgetLine],
    ):

        result = defaultdict(lambda: Decimal("0"))

        for line in budget_lines:
            result[line.company_code] += line.amount

        return dict(result)

        