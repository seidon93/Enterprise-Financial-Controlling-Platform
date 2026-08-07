"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : controller_dashboard_data.py
Object Type     : DTO
Layer           : Service Layer
Version         : 1.8.0
Status          : Development
===============================================================================
"""

from dataclasses import dataclass


@dataclass(slots=True)
class ControllerDashboardData:
    """
    Dashboard data prepared for the presentation layer.
    """

    revenue: float
    expenses: float
    net_profit: float

    current_ratio: float
    quick_ratio: float
    cash_ratio: float

    net_margin: float
    gross_margin: float
    operating_margin: float

    return_on_assets: float
    return_on_equity: float

    inventory_turnover: float
    receivables_turnover: float
    payables_turnover: float
    asset_turnover: float
    inventory_days: float

    working_capital: float
    working_capital_ratio: float

    revenue_budget: float
    revenue_variance: float
    revenue_variance_pct: float

    expense_budget: float
    expense_variance: float
    expense_variance_pct: float