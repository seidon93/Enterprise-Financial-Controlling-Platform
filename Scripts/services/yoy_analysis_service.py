"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : yoy_analysis_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class YoYAnalysis:
    """
    Year-over-Year analysis result.
    """

    current_value: float
    previous_value: float
    absolute_change: float
    change_pct: float
    status: str


class YoYAnalysisService:
    """
    Calculates Year-over-Year changes.
    """

    @staticmethod
    def calculate(
        current_value: float,
        previous_value: float,
    ) -> YoYAnalysis:

        absolute_change = (
            current_value
            - previous_value
        )

        change_pct = (
            absolute_change
            / previous_value
            * 100.0
            if previous_value
            else 0.0
        )

        if absolute_change > 0:
            status = "GROWTH"
        elif absolute_change < 0:
            status = "DECLINE"
        else:
            status = "UNCHANGED"

        return YoYAnalysis(
            current_value=current_value,
            previous_value=previous_value,
            absolute_change=absolute_change,
            change_pct=change_pct,
            status=status,
        )