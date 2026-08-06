import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Scripts')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Scripts.reporting.balance_sheet import BalanceSheet
from Scripts.reporting.income_statement import IncomeStatement
from Scripts.reporting.trial_balance import TrialBalance

from Scripts.services.controller_dashboard import ControllerDashboard
from Scripts.services.financial_controller_report import (
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