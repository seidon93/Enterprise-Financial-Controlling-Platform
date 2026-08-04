from decimal import Decimal

from Scripts.domain.budget import Budget
from Scripts.domain.actual import Actual


def test_budget():

    budget = Budget(

        company_code="CZ01",

        fiscal_year=2025,

        fiscal_period=6,

        cost_center_code="1000",

        account_number="601",

        amount=Decimal("500000"),
    )

    assert budget.amount == Decimal("500000")


def test_actual():

    actual = Actual(

        company_code="CZ01",

        fiscal_year=2025,

        fiscal_period=6,

        cost_center_code="1000",

        account_number="601",

        amount=Decimal("470000"),
    )

    assert actual.amount == Decimal("470000")