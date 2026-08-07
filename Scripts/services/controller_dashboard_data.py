"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : controller_dashboard_data.py
Object Type     : DTO
Layer           : Service Layer
Version         : 1.2.0
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
    net_margin: float
    gross_margin: float
    operating_margin: float
    inventory_turnover: float
    receivables_turnover: float
    payables_turnover: float
    asset_turnover: float
    inventory_days: float