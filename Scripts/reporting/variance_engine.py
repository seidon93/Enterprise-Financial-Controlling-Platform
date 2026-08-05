"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : variance_engine.py
Object Type     : Reporting Engine
Layer           : Reporting
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from decimal import Decimal

try:
    from .variance_result import VarianceResult
except ImportError:
    from variance_result import VarianceResult


class VarianceEngine:

    @staticmethod
    def compare(
        budget: Decimal,
        actual: Decimal,
    ) -> VarianceResult:

        variance = actual - budget

        if budget == Decimal("0"):
            variance_percent = Decimal("0")
        else:
            variance_percent = (
                variance / budget
            ) * Decimal("100")

        return VarianceResult(
            budget=budget,
            actual=actual,
            variance=variance,
            variance_percent=variance_percent,
        )