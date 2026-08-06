from reporting.balance_sheet import BalanceSheet
from reporting.income_statement import IncomeStatement
from reporting.trial_balance import TrialBalance

from services.controller_dashboard import ControllerDashboard
from services.financial_controller_report import (
    FinancialControllerReport,
)


def test_controller_dashboard_creation():

    report = FinancialControllerReport(
        trial_balance=TrialBalance(),
        income_statement=IncomeStatement(),
        balance_sheet=BalanceSheet(),
        financial_ratios={},
    )

    dashboard = ControllerDashboard(
        report=report
    )

    assert dashboard.report is report