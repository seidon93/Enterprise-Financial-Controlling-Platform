"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : controller_dashboard_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from services.controller_dashboard import (
    ControllerDashboard,
)

from services.controller_dashboard_data import (
    ControllerDashboardData,
)

from services.financial_controller_report import (
    FinancialControllerReport,
)


class ControllerDashboardService:

    @staticmethod
    def create(
        report: FinancialControllerReport,
    ) -> ControllerDashboard:

        return ControllerDashboard(
            report=report
        )

    @staticmethod
    def prepare_data(
        report: FinancialControllerReport,
    ) -> ControllerDashboardData:

        return ControllerDashboardData(
            revenue=float(report.income_statement.revenues),
            expenses=float(report.income_statement.expenses),
            net_profit=float(report.income_statement.net_profit),
            current_ratio=report.financial_ratios.get("current_ratio", 0.0),
            net_margin=report.financial_ratios.get("net_margin", 0.0),
        )