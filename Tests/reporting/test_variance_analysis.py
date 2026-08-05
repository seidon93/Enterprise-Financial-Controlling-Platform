import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from Scripts.reporting.variance_analysis import VarianceAnalysis
from decimal import Decimal

def test_variance_by_account():

    budget = {
        "601": Decimal("1000"),
        "602": Decimal("500"),
    }

    actual = {
        "601": Decimal("1200"),
        "602": Decimal("400"),
    }

    rows = VarianceAnalysis.by_account(
        budget,
        actual,
    )

    assert len(rows) == 2

    assert rows[0].key == "601"

    assert rows[0].variance == Decimal("200")


def test_missing_budget_account():

    budget = {}

    actual = {
        "648": Decimal("100"),
    }

    rows = VarianceAnalysis.by_account(
        budget,
        actual,
    )

    assert rows[0].budget == Decimal("0")

    assert rows[0].actual == Decimal("100")


def test_missing_actual_account():

    budget = {
        "521": Decimal("500"),
    }

    actual = {}

    rows = VarianceAnalysis.by_account(
        budget,
        actual,
    )

    assert rows[0].actual == Decimal("0")

    assert rows[0].variance == Decimal("-500")


def test_variance_by_cost_center():

    budget = {
        "100": Decimal("100000"),
        "200": Decimal("80000"),
    }

    actual = {
        "100": Decimal("95000"),
        "200": Decimal("90000"),
    }

    rows = VarianceAnalysis.by_cost_center(
        budget,
        actual,
    )

    assert len(rows) == 2

    assert rows[0].key == "100"


def test_variance_by_department():

    budget = {
        "FIN": Decimal("300000"),
    }

    actual = {
        "FIN": Decimal("315000"),
    }

    rows = VarianceAnalysis.by_department(
        budget,
        actual,
    )

    assert rows[0].variance == Decimal("15000")


def test_variance_by_company():

    budget = {
        "1000": Decimal("1200000"),
    }

    actual = {
        "1000": Decimal("1180000"),
    }

    rows = VarianceAnalysis.by_company(
        budget,
        actual,
    )

    assert rows[0].variance == Decimal("-20000")
