"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : variance_analysis.py
Object Type     : Variance Analysis Engine
Layer           : Reporting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Enterprise variance analysis engine used for controller reporting.
===============================================================================
"""

from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from Scripts.reporting.variace_engine import VarianceEngine



@dataclass(slots=True)
class VarianceAnalysisRow:
    """
    Single variance analysis row.
    """

    key: str

    budget: Decimal

    actual: Decimal

    variance: Decimal

    variance_percent: Decimal


class VarianceAnalysis:
    """
    Enterprise Variance Analysis.
    """

    @staticmethod
    def _analyze(
        budget: dict[str, Decimal],
        actual: dict[str, Decimal],
    ) -> list[VarianceAnalysisRow]:

        rows: list[VarianceAnalysisRow] = []

        keys = sorted(set(budget) | set(actual))

        for key in keys:

            budget_amount = budget.get(key, Decimal("0"))
            actual_amount = actual.get(key, Decimal("0"))

            result = VarianceEngine.calculate(
                budget_amount,
                actual_amount,
            )

            rows.append(
                VarianceAnalysisRow(
                    key=key,
                    budget=budget_amount,
                    actual=actual_amount,
                    variance=result.variance,
                    variance_percent=result.variance_percent,
                )
            )

        return rows

    @staticmethod
    def by_account(
        budget: dict[str, Decimal],
        actual: dict[str, Decimal],
    ) -> list[VarianceAnalysisRow]:

        return VarianceAnalysis._analyze(
            budget,
            actual,
        )

    @staticmethod
    def by_cost_center(
        budget: dict[str, Decimal],
        actual: dict[str, Decimal],
    ) -> list[VarianceAnalysisRow]:

        return VarianceAnalysis._analyze(
            budget,
            actual,
        )

    @staticmethod
    def by_department(
        budget: dict[str, Decimal],
        actual: dict[str, Decimal],
    ) -> list[VarianceAnalysisRow]:

        return VarianceAnalysis._analyze(
            budget,
            actual,
        )

    @staticmethod
    def by_company(
        budget: dict[str, Decimal],
        actual: dict[str, Decimal],
    ) -> list[VarianceAnalysisRow]:

        return VarianceAnalysis._analyze(
            budget,
            actual,
        )