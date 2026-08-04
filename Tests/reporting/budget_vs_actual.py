"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : budget_vs_actual.py
Object Type     : Budget vs Actual Engine
Layer           : Reporting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Calculates Budget vs Actual variance.
===============================================================================
"""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from Scripts.domain.actual import Actual
from Scripts.domain.budget import Budget
from Scripts.domain.variance import Variance


class BudgetVsActualEngine:

    @staticmethod
    def calculate(
        budget: Budget,
        actual: Actual,
    ) -> Variance:

        if budget.amount == Decimal("0"):
            variance_percent = Decimal("0")
        else:
            variance_percent = (
                (actual.amount - budget.amount)
                / budget.amount
            ) * Decimal("100")

        variance = actual.amount - budget.amount

        return Variance(
            company_code=budget.company_code,
            fiscal_year=budget.fiscal_year,
            fiscal_period=budget.fiscal_period,
            cost_center_code=budget.cost_center_code,
            account_number=budget.account_number,
            budget=budget.amount,
            actual=actual.amount,
            variance=variance,
            variance_percent=variance_percent,
            favorable=variance >= Decimal("0"),
        )