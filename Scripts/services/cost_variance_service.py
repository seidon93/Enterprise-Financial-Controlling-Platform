"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : cost_variance_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CostVariance:
    """
    Standard cost versus actual cost variance.
    """

    standard_cost: float
    actual_cost: float
    variance: float
    variance_pct: float
    status: str


class CostVarianceService:
    """
    Calculates standard versus actual cost variance.
    """

    @staticmethod
    def calculate(
        standard_cost: float,
        actual_cost: float,
    ) -> CostVariance:

        standard_cost = standard_cost
        actual_cost = actual_cost

        variance = (
            actual_cost
            - standard_cost
        )

        variance_pct = (
            variance
            / standard_cost
            * 100.0
            if standard_cost
            else 0.0
        )

        if variance == 0:
            status = "ON_TARGET"
        elif variance < 0:
            status = "FAVORABLE"
        else:
            status = "UNFAVORABLE"

        return CostVariance(
            standard_cost=standard_cost,
            actual_cost=actual_cost,
            variance=variance,
            variance_pct=variance_pct,
            status=status,
        )