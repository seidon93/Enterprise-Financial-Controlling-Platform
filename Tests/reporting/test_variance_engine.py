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

from decimal import Decimal

from Scripts.reporting.variance_engine import VarianceEngine


def test_compare_account():

    result = VarianceEngine.compare_account(
        account_code="601",
        budget=Decimal("100000"),
        actual=Decimal("120000"),
    )

    assert result.account_code == "601"

    assert result.variance == Decimal("20000")

    assert result.favorable is True

def test_compare_account_unfavorable():

    result = VarianceEngine.compare_account(
        account_code="521",
        budget=Decimal("400000"),
        actual=Decimal("460000"),
    )

    assert result.account_code == "521"

    assert result.variance == Decimal("60000")

    # vyšší mzdové náklady jsou nepříznivé
    assert result.favorable is False