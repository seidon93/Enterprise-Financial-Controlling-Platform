from decimal import Decimal

from Scripts.reporting.management_report import ManagementReport


def test_management_report():

    budget = {
        "601": Decimal("1000"),
        "521": Decimal("600"),
    }

    actual = {
        "601": Decimal("1200"),
        "521": Decimal("700"),
    }

    report = ManagementReport.create(
        budget,
        actual,
        revenue_accounts={"601"},
    )

    assert len(report) == 2

    assert report[0].status == "Unfavorable"

    assert report[1].status == "Favorable"