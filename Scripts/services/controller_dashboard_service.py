"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : controller_dashboard_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 2.0.0
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

        revenue = float(report.income_statement.revenue)
        expenses = float(report.income_statement.expenses)

        revenue_budget = float(
            getattr(report, "revenue_budget", 0.0)
        )

        expense_budget = float(
            getattr(report, "expense_budget", 0.0)
        )

        revenue_variance = revenue - revenue_budget
        expense_variance = expenses - expense_budget

        revenue_variance_pct = (
            revenue_variance / revenue_budget * 100.0
            if revenue_budget
            else 0.0
        )

        expense_variance_pct = (
            expense_variance / expense_budget * 100.0
            if expense_budget
            else 0.0
        )

        return ControllerDashboardData(
            revenue=revenue,
            expenses=expenses,
            net_profit=float(report.income_statement.net_profit),

            current_ratio=float(ratios["current_ratio"]),
            quick_ratio=float(ratios["quick_ratio"]),
            cash_ratio=float(ratios["cash_ratio"]),

            net_margin=float(ratios["net_margin"]),
            gross_margin=float(ratios["gross_margin"]),
            operating_margin=float(ratios["operating_margin"]),

            return_on_assets=float(
                ratios["return_on_assets"]
            ),
            return_on_equity=float(
                ratios["return_on_equity"]
            ),

            inventory_turnover=float(
                ratios["inventory_turnover"]
            ),
            receivables_turnover=float(
                ratios["receivables_turnover"]
            ),
            payables_turnover=float(
                ratios["payables_turnover"]
            ),
            asset_turnover=float(
                ratios["asset_turnover"]
            ),
            inventory_days=float(
                ratios["inventory_days"]
            ),

            working_capital=float(
                ratios["working_capital"]
            ),
            working_capital_ratio=float(
                ratios["working_capital_ratio"]
            ),

            revenue_budget=revenue_budget,
            revenue_variance=revenue_variance,
            revenue_variance_pct=revenue_variance_pct,

            expense_budget=expense_budget,
            expense_variance=expense_variance,
            expense_variance_pct=expense_variance_pct,
        )