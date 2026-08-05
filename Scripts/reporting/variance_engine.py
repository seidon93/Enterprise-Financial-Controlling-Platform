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
            account_code="",
            budget=budget,
            actual=actual,
            variance=variance,
            variance_percent=variance_percent,
            favorable=variance >= Decimal("0"),
        )

    @staticmethod
    def compare_account(
        *,
        account_code: str,
        budget: Decimal,
        actual: Decimal,
    ) -> VarianceResult:

        variance = actual - budget

        if budget == Decimal("0"):
            percent = Decimal("0")
        else:
            percent = variance / budget * Decimal("100")

        return VarianceResult(
            account_code=account_code,
            budget=budget,
            actual=actual,
            variance=variance,
            variance_percent=percent,
            favorable=variance <= Decimal("0") if account_code.startswith("5") else variance >= Decimal("0"),
        )