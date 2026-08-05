from decimal import Decimal

from Scripts.reporting.variance_engine import VarianceEngine


def test_variance_positive():

    result = VarianceEngine.compare(
        budget=Decimal("100000"),
        actual=Decimal("120000"),
    )

    assert result.budget == Decimal("100000")
    assert result.actual == Decimal("120000")
    assert result.variance == Decimal("20000")
    assert result.variance_percent == Decimal("20")


def test_variance_negative():

    result = VarianceEngine.compare(
        budget=Decimal("100000"),
        actual=Decimal("80000"),
    )

    assert result.variance == Decimal("-20000")
    assert result.variance_percent == Decimal("-20")


def test_zero_budget():

    result = VarianceEngine.compare(
        budget=Decimal("0"),
        actual=Decimal("5000"),
    )

    assert result.variance == Decimal("5000")
    assert result.variance_percent == Decimal("0")