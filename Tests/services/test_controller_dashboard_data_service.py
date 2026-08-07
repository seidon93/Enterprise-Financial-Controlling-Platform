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


def test_prepare_controller_dashboard_data():

    tb = TrialBalance()
    tb._accounts["6000"] = Decimal("-1000000") # revenues
    tb._accounts["5000"] = Decimal("800000")   # expenses
    tb._accounts["1000"] = Decimal("250000")   # assets
    tb._accounts["3000"] = Decimal("-100000")  # liabilities

    income_statement = IncomeStatement(tb)
    balance_sheet = BalanceSheet(tb)

    report = FinancialControllerReport(
        trial_balance=tb,
        income_statement=income_statement,
        balance_sheet=balance_sheet,
        financial_ratios={
            "current_ratio": 2.5,
            "net_margin": 20.0,
            "gross_margin": 35.0,
            "operating_margin": 22.0,
        },
    )

    data = ControllerDashboardService.prepare_data(
        report
    )

    assert data.revenue == 1000000.0
    assert data.expenses == 800000.0
    assert data.net_profit == 200000.0
    assert data.current_ratio == 2.5
    assert data.net_margin == 20.0