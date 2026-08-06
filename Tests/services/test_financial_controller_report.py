from tests.services.financial_controller_report import FinancialControllerReport

from Scripts.reporting.trial_balance import TrialBalance
from Scripts.reporting.income_statement import IncomeStatement
from Scripts.reporting.balance_sheet import BalanceSheet


def test_financial_controller_report_creation():

    tb = TrialBalance()
    report = FinancialControllerReport(
        trial_balance=tb,
        income_statement=IncomeStatement(tb),
        balance_sheet=BalanceSheet(tb),
    )

    assert report.trial_balance is not None
    assert report.income_statement is not None
    assert report.balance_sheet is not None