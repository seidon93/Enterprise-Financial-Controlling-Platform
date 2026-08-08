"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : controller_dashboard_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 2.8.0
Status          : Development
===============================================================================
"""

from services.budget_variance_service import (
    BudgetVarianceService,
)
from services.controller_dashboard import ControllerDashboard
from services.controller_dashboard_data import ControllerDashboardData
from services.controller_dashboard_summary_service import (
    ControllerDashboardSummaryService,
)
from services.cost_variance_service import (
    CostVarianceService,
)
from services.financial_controller_report import (
    FinancialControllerReport,
)
from services.price_volume_analysis_service import (
    PriceVolumeAnalysisService,
)
from services.yoy_analysis_service import (
    YoYAnalysisService,
)


class ControllerDashboardService:

    @staticmethod
    def create(
        report: FinancialControllerReport,
    ) -> ControllerDashboard:

        data = ControllerDashboardService.prepare_data(
            report
        )

        summary = ControllerDashboardSummaryService.create(
            data
        )

        return ControllerDashboard(
            report=report,
            data=data,
            summary=summary,
        )

    @staticmethod
    def prepare_data(
        report: FinancialControllerReport,
    ) -> ControllerDashboardData:

        ratios = report.financial_ratios

        revenue = float(
            report.income_statement.revenue
        )

        expenses = float(
            report.income_statement.expenses
        )

        net_profit = float(
            report.income_statement.net_profit
        )

        revenue_variance = BudgetVarianceService.calculate(
            budget=report.revenue_budget,
            actual=revenue,
            favorable_when="higher",
        )

        expense_variance = BudgetVarianceService.calculate(
            budget=report.expense_budget,
            actual=expenses,
            favorable_when="lower",
        )

        budget_net_profit = (
            report.revenue_budget
            - report.expense_budget
        )

        net_profit_variance = BudgetVarianceService.calculate(
            budget=budget_net_profit,
            actual=net_profit,
            favorable_when="higher",
        )

        revenue_yoy = YoYAnalysisService.calculate(
            current_value=revenue,
            previous_value=report.revenue_previous_year,
        )

        net_profit_yoy = YoYAnalysisService.calculate(
            current_value=net_profit,
            previous_value=report.net_profit_previous_year,
        )

        price_volume = PriceVolumeAnalysisService.calculate(
            previous_price=report.previous_price,
            current_price=report.current_price,
            previous_volume=report.previous_volume,
            current_volume=report.current_volume,
            previous_revenue=report.revenue_previous_year,
            current_revenue=revenue,
        )

        cost_variance = CostVarianceService.calculate(
            standard_cost=report.standard_cost,
            actual_cost=report.actual_cost,
        )

        return ControllerDashboardData(
            revenue=revenue,
            expenses=expenses,
            net_profit=net_profit,

            current_ratio=ratios["current_ratio"],
            quick_ratio=ratios["quick_ratio"],
            cash_ratio=ratios["cash_ratio"],

            net_margin=ratios["net_margin"],
            gross_margin=ratios["gross_margin"],
            operating_margin=ratios["operating_margin"],

            return_on_assets=ratios["return_on_assets"],
            return_on_equity=ratios["return_on_equity"],

            inventory_turnover=ratios["inventory_turnover"],
            receivables_turnover=ratios["receivables_turnover"],
            payables_turnover=ratios["payables_turnover"],
            asset_turnover=ratios["asset_turnover"],
            inventory_days=ratios["inventory_days"],

            working_capital=ratios["working_capital"],
            working_capital_ratio=ratios["working_capital_ratio"],

            revenue_budget=revenue_variance.budget,
            revenue_variance=revenue_variance.variance,
            revenue_variance_pct=revenue_variance.variance_pct,
            revenue_variance_status=revenue_variance.status,

            expense_budget=expense_variance.budget,
            expense_variance=expense_variance.variance,
            expense_variance_pct=expense_variance.variance_pct,
            expense_variance_status=expense_variance.status,

            budget_net_profit=net_profit_variance.budget,
            net_profit_variance=net_profit_variance.variance,
            net_profit_variance_pct=net_profit_variance.variance_pct,
            net_profit_variance_status=net_profit_variance.status,

            revenue_previous_year=revenue_yoy.previous_value,
            revenue_yoy_change=revenue_yoy.absolute_change,
            revenue_yoy_change_pct=revenue_yoy.change_pct,
            revenue_yoy_status=revenue_yoy.status,

            net_profit_previous_year=net_profit_yoy.previous_value,
            net_profit_yoy_change=net_profit_yoy.absolute_change,
            net_profit_yoy_change_pct=net_profit_yoy.change_pct,
            net_profit_yoy_status=net_profit_yoy.status,

            previous_price=price_volume.previous_price,
            current_price=price_volume.current_price,
            previous_volume=price_volume.previous_volume,
            current_volume=price_volume.current_volume,

            price_effect=price_volume.price_effect,
            volume_effect=price_volume.volume_effect,
            total_revenue_change=price_volume.total_revenue_change,

            standard_cost=cost_variance.standard_cost,
            actual_cost=cost_variance.actual_cost,
            cost_variance=cost_variance.variance,
            cost_variance_pct=cost_variance.variance_pct,
            cost_variance_status=cost_variance.status,
        )