from decimal import Decimal

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

def test_monthly_report():

    report = FinancialControllerService.create_monthly_report(
        trial_balance=None,
        income_statement=None,
        balance_sheet=None,
        variances=[],
        ratios={
            "Current Ratio": Decimal("2.1"),
            "ROE": Decimal("18.4"),
        },
    )

    assert report.ratios["ROE"] == Decimal("18.4")

    assert report.ratios["Current Ratio"] == Decimal("2.1")

    assert "variances" in report.executive_summary