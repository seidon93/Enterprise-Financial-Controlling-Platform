"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : controller_dashboard.py
Object Type     : DTO
Layer           : Service Layer
Version         : 1.1.0
Status          : Development
===============================================================================
"""

from dataclasses import dataclass

from services.controller_dashboard_data import (
    ControllerDashboardData,
)
from services.controller_dashboard_summary_service import (
    ControllerDashboardSummary,
)


@dataclass(slots=True)
class ControllerDashboard:
    """
    Complete controller dashboard.
    """

    report: object
    data: ControllerDashboardData
    summary: ControllerDashboardSummary | None = None