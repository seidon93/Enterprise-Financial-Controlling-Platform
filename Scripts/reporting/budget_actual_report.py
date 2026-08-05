"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : budget_actual_report.py
Object Type     : Budget vs Actual Report
Layer           : Reporting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Enterprise Budget vs Actual reporting engine.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from Scripts.reporting.variance_analysis import VarianceAnalysis


@dataclass(slots=True)
class BudgetActualReportRow:
    """
    Single Budget vs Actual report row.
    """

    key: str

    budget: Decimal

    actual: Decimal

    variance: Decimal

    variance_percent: Decimal


class BudgetActualReport:
    """
    Enterprise Budget vs Actual Report.
    """

    @staticmethod
    def create(
        budget: dict[str, Decimal],
        actual: dict[str, Decimal],
    ) -> list[BudgetActualReportRow]:

        analysis = VarianceAnalysis.by_account(
            budget,
            actual,
        )

        report: list[BudgetActualReportRow] = []

        for row in analysis:

            report.append(
                BudgetActualReportRow(
                    key=row.key,
                    budget=row.budget,
                    actual=row.actual,
                    variance=row.variance,
                    variance_percent=row.variance_percent,
                )
            )

        return report