from reporting.balance_sheet import BalanceSheet
from reporting.income_statement import IncomeStatement
from reporting.trial_balance import TrialBalance

from services.financial_controller_report import (
    FinancialControllerReport,
)


def test_financial_controller_report_budget_values():

    report = FinancialControllerReport(
        trial_balance=TrialBalance(),
        income_statement=IncomeStatement(),
        balance_sheet=BalanceSheet(),
        financial_ratios={},
        revenue_budget=950000.0,
        expense_budget=750000.0,
    )

    assert report.revenue_budget == 950000.0
    assert report.expense_budget == 750000.0