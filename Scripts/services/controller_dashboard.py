"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : controller_dashboard.py
Object Type     : Service
Layer           : Service Layer
Version         : 1.1.0
Status          : Development
===============================================================================
"""

from dataclasses import dataclass

from services.controller_dashboard_data import (
    ControllerDashboardData,
)

from services.financial_controller_report import (
    FinancialControllerReport,
)


@dataclass(slots=True)
class ControllerDashboard:
    """
    Enterprise Financial Controller Dashboard.
    """

    report: FinancialControllerReport
    data: ControllerDashboardData