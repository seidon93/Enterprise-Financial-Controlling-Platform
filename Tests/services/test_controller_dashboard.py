from reporting.balance_sheet import BalanceSheet
from reporting.income_statement import IncomeStatement
from reporting.trial_balance import TrialBalance
from services.controller_dashboard import ControllerDashboard
from services.controller_dashboard_data import ControllerDashboardData
from services.financial_controller_report import FinancialControllerReport


def test_controller_dashboard_creation():

    tb = TrialBalance()

    report = FinancialControllerReport(
        trial_balance=tb,
        income_statement=IncomeStatement(tb),
        balance_sheet=BalanceSheet(tb),
        financial_ratios={},
    )

    data = ControllerDashboardData(
        revenue=100.0,
        expenses=50.0,
        net_profit=50.0,
        current_ratio=1.0,
        net_margin=0.5,
        gross_margin=0.6,
        operating_margin=0.4,
        inventory_turnover=4.0,
        receivables_turnover=6.0,
        payables_turnover=5.0,
        asset_turnover=0.5,
        inventory_days=91.25,
        working_capital=150000.0,
        working_capital_ratio=1.5,
        cash_ratio=0.8,
        quick_ratio=2.0,
        return_on_assets=9.0,
        return_on_equity=20.0,
        revenue_budget=950000.0,
        revenue_variance=50000.0,
        revenue_variance_pct=5.26,
        expense_budget=750000.0,
        expense_variance=50000.0,
        expense_variance_pct=6.66,
        budget_net_profit=200000.0,
        net_profit_variance=0.0,
        net_profit_variance_pct=0.0,
    )

    dashboard = ControllerDashboard(
        report=report,
        data=data,
    )

    assert dashboard.report is report
    assert dashboard.data is data