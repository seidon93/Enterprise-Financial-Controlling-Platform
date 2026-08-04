import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from decimal import Decimal

from Scripts.budget.budget import Budget
from Scripts.budget.budget_line import BudgetLine
from Scripts.budget.budget_repository import BudgetRepository
from Scripts.budget.budget_version import BudgetVersion


def create_budget() -> Budget:

    budget = Budget(
        name="FY2025 Original Budget",
        fiscal_year=2025,
        version=BudgetVersion.ORIGINAL,
    )

    budget.add_line(
        BudgetLine(
            company_code="CZ01",
            account_number="601",
            cost_center_code="CC100",
            department_code="FIN",
            fiscal_year=2025,
            fiscal_period=1,
            amount=Decimal("100000"),
        )
    )

    return budget


def test_add_budget():

    repository = BudgetRepository()

    budget = create_budget()

    repository.add(budget)

    assert len(repository.get_all()) == 1