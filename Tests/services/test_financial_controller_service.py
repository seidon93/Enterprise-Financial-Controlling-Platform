from Scripts.services.financial_controller_service import (
    FinancialControllerService,
)

from Scripts.services.models import FinancialControllerReport


def test_create_report():

    report = FinancialControllerService.create_report(
        trial_balance=None,
        income_statement=None,
        balance_sheet=None,
        variances=[],
    )

    assert isinstance(
        report,
        FinancialControllerReport,
    )

    assert report.variances == []