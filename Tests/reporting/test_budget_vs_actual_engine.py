import sys
from decimal import Decimal
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from Scripts.domain.actual import Actual
from Scripts.domain.budget import Budget
from tests.reporting.budget_vs_actual import BudgetVsActualEngine


def test_budget_vs_actual():

    budget = Budget(
        company_code="CZ01",
        fiscal_year=2025,
        fiscal_period=6,
        cost_center_code="1000",
        account_number="601",
        amount=Decimal("500000"),
    )

    actual = Actual(
        company_code="CZ01",
        fiscal_year=2025,
        fiscal_period=6,
        cost_center_code="1000",
        account_number="601",
        amount=Decimal("470000"),
    )

    result = BudgetVsActualEngine.calculate(
        budget,
        actual,
    )

    assert result.variance == Decimal("-30000")
    assert result.variance_percent == Decimal("-6")
    assert result.favorable is False


def test_positive_variance():

    budget = Budget(
        company_code="CZ01",
        fiscal_year=2025,
        fiscal_period=6,
        cost_center_code="1000",
        account_number="601",
        amount=Decimal("500000"),
    )

    actual = Actual(
        company_code="CZ01",
        fiscal_year=2025,
        fiscal_period=6,
        cost_center_code="1000",
        account_number="601",
        amount=Decimal("550000"),
    )

    result = BudgetVsActualEngine.calculate(
        budget,
        actual,
    )

    assert result.variance == Decimal("50000")
    assert result.variance_percent == Decimal("10")
    assert result.favorable is True