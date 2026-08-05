"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : management_report.py
Object Type     : Management Report
Layer           : Reporting
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from Scripts.reporting.budget_actual_report import BudgetActualReport
from Scripts.reporting.variance_explanation import VarianceExplanation


@dataclass(slots=True)
class ManagementReportRow:

    key: str

    budget: Decimal

    actual: Decimal

    variance: Decimal

    variance_percent: Decimal

    status: str


class ManagementReport:

    @staticmethod
    def create(
        budget: dict[str, Decimal],
        actual: dict[str, Decimal],
        revenue_accounts: set[str] | None = None,
    ) -> list[ManagementReportRow]:

        revenue_accounts = revenue_accounts or set()

        report = BudgetActualReport.create(
            budget,
            actual,
        )

        rows: list[ManagementReportRow] = []

        for row in report:

            rows.append(
                ManagementReportRow(
                    key=row.key,
                    budget=row.budget,
                    actual=row.actual,
                    variance=row.variance,
                    variance_percent=row.variance_percent,
                    status=VarianceExplanation.explain(
                        row.variance,
                        revenue_account=row.key in revenue_accounts,
                    ),
                )
            )

        return rows