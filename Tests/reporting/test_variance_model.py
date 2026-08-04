from decimal import Decimal

from Scripts.domain.variance import Variance


def test_variance_model():

    variance = Variance(

        company_code="CZ01",

        fiscal_year=2025,

        fiscal_period=6,

        cost_center_code="1000",

        account_number="601",

        budget=Decimal("500000"),

        actual=Decimal("470000"),

        variance=Decimal("-30000"),

        variance_percent=Decimal("-6"),

        favorable=False,
    )

    assert variance.variance == Decimal("-30000")

    assert variance.favorable is False