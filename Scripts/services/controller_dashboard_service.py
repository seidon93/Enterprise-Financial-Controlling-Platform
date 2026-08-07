"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : controller_dashboard_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 1.4.0
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

        ratios = report.financial_ratios

        return ControllerDashboardData(
            revenue=float(report.income_statement.revenue),
            expenses=float(report.income_statement.expenses),
            net_profit=float(report.income_statement.net_profit),
            current_ratio=ratios["current_ratio"],
            net_margin=ratios["net_margin"],
            gross_margin=ratios["gross_margin"],
            operating_margin=ratios["operating_margin"],
            inventory_turnover=ratios["inventory_turnover"],
            receivables_turnover=ratios["receivables_turnover"],
            payables_turnover=ratios["payables_turnover"],
            asset_turnover=ratios["asset_turnover"],
            inventory_days=ratios["inventory_days"],
        )