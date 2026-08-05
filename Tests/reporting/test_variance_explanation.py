from decimal import Decimal

from Scripts.reporting.variance_explanation import VarianceExplanation


def test_revenue_favorable():

    assert (
        VarianceExplanation.explain(
            Decimal("100"),
            revenue_account=True,
        )
        == "Favorable"
    )


def test_revenue_unfavorable():

    assert (
        VarianceExplanation.explain(
            Decimal("-100"),
            revenue_account=True,
        )
        == "Unfavorable"
    )


def test_cost_favorable():

    assert (
        VarianceExplanation.explain(
            Decimal("-100"),
        )
        == "Favorable"
    )


def test_cost_unfavorable():

    assert (
        VarianceExplanation.explain(
            Decimal("100"),
        )
        == "Unfavorable"
    )


def test_on_target():

    assert (
        VarianceExplanation.explain(
            Decimal("0"),
        )
        == "On Target"
    )