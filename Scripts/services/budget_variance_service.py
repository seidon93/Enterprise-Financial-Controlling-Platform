"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : budget_variance_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BudgetVariance:
    """
    Budget versus actual variance result.
    """

    budget: float
    actual: float
    variance: float
    variance_pct: float
    status: str


class BudgetVarianceService:
    """
    Calculates budget versus actual variances.
    """

    @staticmethod
    def calculate(
        budget: float,
        actual: float,
        favorable_when: str,
    ) -> BudgetVariance:

        variance = actual - budget

        variance_pct = (
            variance / budget * 100.0
            if budget
            else 0.0
        )

        if variance == 0:
            status = "ON_TARGET"

        elif favorable_when == "higher":
            status = (
                "FAVORABLE"
                if variance > 0
                else "UNFAVORABLE"
            )

        elif favorable_when == "lower":
            status = (
                "FAVORABLE"
                if variance < 0
                else "UNFAVORABLE"
            )

        else:
            raise ValueError(
                "favorable_when must be 'higher' or 'lower'"
            )

        return BudgetVariance(
            budget=budget,
            actual=actual,
            variance=variance,
            variance_pct=variance_pct,
            status=status,
        )