import sys
from decimal import Decimal
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

import pytest

from Scripts.budget.budget import Budget
from Scripts.budget.budget_line import BudgetLine
from Scripts.budget.budget_validator import (
    BudgetValidator,
    BudgetValidationError,
)
from Scripts.budget.budget_version import BudgetVersion


def create_budget():

    return Budget(
        name="Budget",
        fiscal_year=2026,
        version=BudgetVersion.ORIGINAL,
    )


def create_line(amount=Decimal("100")):

    return BudgetLine(
        company_code="CZ01",
        account_number="601000",
        cost_center_code="SALES",
        department_code="COMMERCIAL",
        fiscal_year=2026,
        fiscal_period=1,
        amount=amount,
    )


def test_valid_budget():

    budget = create_budget()

    budget.add_line(create_line())

    BudgetValidator.validate(budget)


def test_budget_without_lines():

    budget = create_budget()

    with pytest.raises(BudgetValidationError):

        BudgetValidator.validate(budget)


def test_negative_amount():

    budget = create_budget()

    budget.add_line(create_line(Decimal("-100")))

    with pytest.raises(BudgetValidationError):

        BudgetValidator.validate(budget)


def test_missing_account():

    budget = create_budget()

    line = create_line()

    line.account_number = ""

    budget.add_line(line)

    with pytest.raises(BudgetValidationError):

        BudgetValidator.validate(budget)


def test_invalid_period():

    budget = create_budget()

    line = create_line()

    line.fiscal_period = 15

    budget.add_line(line)

    with pytest.raises(BudgetValidationError):

        BudgetValidator.validate(budget)