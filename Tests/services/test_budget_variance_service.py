from services.budget_variance_service import (
    BudgetVarianceService,
)


def test_revenue_variance_favorable_when_actual_is_higher():

    result = BudgetVarianceService.calculate(
        budget=950000.0,
        actual=1000000.0,
        favorable_when="higher",
    )

    assert result.budget == 950000.0
    assert result.actual == 1000000.0
    assert result.variance == 50000.0
    assert result.status == "FAVORABLE"


def test_expense_variance_favorable_when_actual_is_lower():

    result = BudgetVarianceService.calculate(
        budget=750000.0,
        actual=700000.0,
        favorable_when="lower",
    )

    assert result.budget == 750000.0
    assert result.actual == 700000.0
    assert result.variance == -50000.0
    assert result.status == "FAVORABLE"


def test_zero_variance_is_on_target():

    result = BudgetVarianceService.calculate(
        budget=500000.0,
        actual=500000.0,
        favorable_when="higher",
    )

    assert result.variance == 0.0
    assert result.variance_pct == 0.0
    assert result.status == "ON_TARGET"


def test_invalid_favorable_direction():

    try:
        BudgetVarianceService.calculate(
            budget=100.0,
            actual=110.0,
            favorable_when="invalid",
        )
    except ValueError as exc:
        assert str(exc) == (
            "favorable_when must be 'higher' or 'lower'"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )