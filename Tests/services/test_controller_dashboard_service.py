from reporting.balance_sheet import BalanceSheet
from reporting.income_statement import IncomeStatement
from reporting.trial_balance import TrialBalance

from services.controller_dashboard_service import (
    ControllerDashboardService,
)
from services.financial_controller_report import (
    FinancialControllerReport,
)


def create_report() -> FinancialControllerReport:
    from decimal import Decimal
    tb = TrialBalance()
    tb._accounts["6000"] = Decimal("-1000000") # revenues
    tb._accounts["5000"] = Decimal("800000")   # expenses
    tb._accounts["1000"] = Decimal("250000")   # assets
    tb._accounts["3000"] = Decimal("-100000")  # liabilities

    return FinancialControllerReport(
        trial_balance=tb,
        income_statement=IncomeStatement(tb),
        balance_sheet=BalanceSheet(tb),
        financial_ratios={
            "current_ratio": 2.5,
            "quick_ratio": 2.0,
            "cash_ratio": 0.8,
            "net_margin": 20.0,
            "gross_margin": 35.0,
            "operating_margin": 22.0,
            "return_on_assets": 9.0,
            "return_on_equity": 20.0,
            "inventory_turnover": 4.0,
            "receivables_turnover": 6.0,
            "payables_turnover": 5.0,
            "asset_turnover": 0.5,
            "inventory_days": 91.25,
            "working_capital": 150000.0,
            "working_capital_ratio": 1.5,
        },
        revenue_budget=950000.0,
        expense_budget=750000.0,
    )


def test_create_controller_dashboard():

    report = create_report()

    dashboard = ControllerDashboardService.create(
        report
    )

    assert dashboard.report is report
    assert dashboard.data is not None


def test_prepare_data_revenue_variance():

    report = create_report()

    data = ControllerDashboardService.prepare_data(
        report
    )

    assert data.revenue_budget == 950000.0
    assert data.revenue_variance == 50000.0
    assert data.revenue_variance_pct > 5.0
    assert data.revenue_variance_status == "FAVORABLE"


def test_prepare_data_expense_variance():

    report = create_report()

    data = ControllerDashboardService.prepare_data(
        report
    )

    assert data.expense_budget == 750000.0
    assert data.expense_variance == 50000.0
    assert data.expense_variance_pct > 6.0
    assert data.expense_variance_status == "UNFAVORABLE"


def test_prepare_data_budget_net_profit():

    report = create_report()

    data = ControllerDashboardService.prepare_data(
        report
    )

    assert data.budget_net_profit == 200000.0
    assert data.net_profit_variance == 0.0
    assert data.net_profit_variance_pct == 0.0
    assert data.net_profit_variance_status == "ON_TARGET"