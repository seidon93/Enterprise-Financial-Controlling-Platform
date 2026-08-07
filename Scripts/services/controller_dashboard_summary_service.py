"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : controller_dashboard_summary_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from dataclasses import dataclass

from services.controller_dashboard_data import (
    ControllerDashboardData,
)


@dataclass(frozen=True, slots=True)
class ControllerDashboardSummary:
    """
    Executive summary prepared for the controller dashboard.
    """

    revenue: float
    expenses: float
    net_profit: float

    revenue_budget_variance: float
    revenue_yoy_change_pct: float

    expense_budget_variance: float
    net_profit_budget_variance: float
    net_profit_yoy_change_pct: float

    price_effect: float
    volume_effect: float
    cost_variance: float

    overall_status: str


class ControllerDashboardSummaryService:
    """
    Builds the executive controller dashboard summary.
    """

    @staticmethod
    def create(
        data: ControllerDashboardData,
    ) -> ControllerDashboardSummary:

        statuses = (
            data.revenue_variance_status,
            data.expense_variance_status,
            data.net_profit_variance_status,
            data.revenue_yoy_status,
            data.net_profit_yoy_status,
            data.cost_variance_status,
        )

        unfavorable_count = statuses.count(
            "UNFAVORABLE"
        )

        if unfavorable_count == 0:
            overall_status = "FAVORABLE"

        elif unfavorable_count <= 2:
            overall_status = "ATTENTION"

        else:
            overall_status = "UNFAVORABLE"

        return ControllerDashboardSummary(
            revenue=data.revenue,
            expenses=data.expenses,
            net_profit=data.net_profit,

            revenue_budget_variance=(
                data.revenue_variance
            ),
            revenue_yoy_change_pct=(
                data.revenue_yoy_change_pct
            ),

            expense_budget_variance=(
                data.expense_variance
            ),
            net_profit_budget_variance=(
                data.net_profit_variance
            ),
            net_profit_yoy_change_pct=(
                data.net_profit_yoy_change_pct
            ),

            price_effect=data.price_effect,
            volume_effect=data.volume_effect,
            cost_variance=data.cost_variance,

            overall_status=overall_status,
        )