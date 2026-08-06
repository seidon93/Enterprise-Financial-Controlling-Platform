import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.financial_controller_report import (
    FinancialControllerReport,
)

from reporting.trial_balance import TrialBalance
from reporting.income_statement import IncomeStatement
from reporting.balance_sheet import BalanceSheet


def test_financial_controller_report_creation():

    tb = TrialBalance()
    report = FinancialControllerReport(
        trial_balance=tb,
        income_statement=IncomeStatement(tb),
        balance_sheet=BalanceSheet(tb),
        financial_ratios={},
    )

    assert report.trial_balance is not None
    assert report.income_statement is not None
    assert report.balance_sheet is not None
    assert report.financial_ratios == {}