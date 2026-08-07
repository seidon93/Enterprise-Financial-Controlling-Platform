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
    report = FinancialControllerReport(
        trial_balance=tb,
        income_statement=IncomeStatement(tb),
        balance_sheet=BalanceSheet(tb),
        financial_ratios={
            "current_ratio": 2.5,
            "net_margin": 20.0,
            "gross_margin": 35.0,
            "operating_margin": 22.0,
        },
    )

    dashboard = ControllerDashboardService.create(
        report
    )

    assert dashboard.report is report