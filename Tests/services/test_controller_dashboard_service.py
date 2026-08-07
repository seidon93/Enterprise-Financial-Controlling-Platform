from decimal import Decimal
from reporting.balance_sheet import BalanceSheet
from reporting.income_statement import IncomeStatement
from reporting.trial_balance import TrialBalance

from services.controller_dashboard_service import (
    ControllerDashboardService,
)

from services.financial_controller_report import (
    FinancialControllerReport,
)


def test_create_controller_dashboard():

    tb = TrialBalance()
    tb._accounts["6000"] = Decimal("-1000000") # revenues
    tb._accounts["5000"] = Decimal("800000")   # expenses
    tb._accounts["1000"] = Decimal("250000")   # assets
    tb._accounts["3000"] = Decimal("-100000")  # liabilities

    report = FinancialControllerReport(
        trial_balance=tb,
        income_statement=IncomeStatement(tb),
        balance_sheet=BalanceSheet(tb),
        financial_ratios={
            "current_ratio": 2.5,
            "net_margin": 20.0,
            "gross_margin": 35.0,
            "operating_margin": 22.0,
            "inventory_turnover": 4.0,
            "receivables_turnover": 6.0,
            "payables_turnover": 5.0,
            "asset_turnover": 0.5,
            "inventory_days": 91.25,
            "working_capital": 150000.0,
            "working_capital_ratio": 1.5,
            "cash_ratio": 0.8,
            "quick_ratio": 2.0,
            "return_on_assets": 9.0,
            "return_on_equity": 20.0,
        },
    )

    dashboard = ControllerDashboardService.create(
        report
    )

    assert dashboard.report is report
    assert dashboard.data is not None
    assert dashboard.data.current_ratio == 2.5
    assert dashboard.data.net_margin == 20.0
    assert dashboard.data.gross_margin == 35.0
    assert dashboard.data.operating_margin == 22.0
    assert dashboard.data.return_on_assets == 9.0
    assert dashboard.data.return_on_equity == 20.0