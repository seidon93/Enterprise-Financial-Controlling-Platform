"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : controller_dashboard_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 1.2.0
Status          : Development
===============================================================================
"""

from services.controller_dashboard import ControllerDashboard
from services.controller_dashboard_data import ControllerDashboardData
from services.financial_controller_report import FinancialControllerReport


class ControllerDashboardService:

    @staticmethod
    def create(
        report: FinancialControllerReport,
    ) -> ControllerDashboard:

        data = ControllerDashboardService.prepare_data(
            report
        )

        return ControllerDashboard(
            report=report,
            data=data,
        )

    @staticmethod
    def prepare_data(
        report: FinancialControllerReport,
    ) -> ControllerDashboardData:

        return ControllerDashboardData(
            revenue=float(report.income_statement.revenues),
            expenses=float(report.income_statement.expenses),
            net_profit=float(report.income_statement.net_profit),
            current_ratio=report.financial_ratios["current_ratio"],
            net_margin=report.financial_ratios["net_margin"],
        )