from decimal import Decimal

from Scripts.reporting.budget_actual_report import BudgetActualReport


def test_budget_actual_report():

    budget = {
        "601": Decimal("1000"),
        "602": Decimal("500"),
    }

    actual = {
        "601": Decimal("1200"),
        "602": Decimal("400"),
    }

    report = BudgetActualReport.create(
        budget,
        actual,
    )

    assert len(report) == 2

    assert report[0].key == "601"

    assert report[0].budget == Decimal("1000")

    assert report[0].actual == Decimal("1200")

    assert report[0].variance == Decimal("200")

    assert report[0].variance_percent == Decimal("20")


def test_budget_actual_missing_budget():

    budget = {}

    actual = {
        "648": Decimal("150"),
    }

    report = BudgetActualReport.create(
        budget,
        actual,
    )

    assert report[0].budget == Decimal("0")

    assert report[0].actual == Decimal("150")


def test_budget_actual_missing_actual():

    budget = {
        "521": Decimal("300"),
    }

    actual = {}

    report = BudgetActualReport.create(
        budget,
        actual,
    )

    assert report[0].actual == Decimal("0")

    assert report[0].variance == Decimal("-300")