import sys
from decimal import Decimal
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from Scripts.budget.budget import Budget
from Scripts.budget.budget_line import BudgetLine
from Scripts.budget.budget_version import BudgetVersion


def test_create_budget():

    budget = Budget(

        name="2026 Budget",

        fiscal_year=2026,

        version=BudgetVersion.ORIGINAL,
    )

    assert budget.name == "2026 Budget"

    assert budget.version == BudgetVersion.ORIGINAL


def test_add_budget_line():

    budget = Budget(

        name="Budget",

        fiscal_year=2026,

        version=BudgetVersion.ORIGINAL,
    )

    budget.add_line(

        BudgetLine(

            company_code="CZ01",

            account_number="601000",

            cost_center_code="SALES",

            department_code="COMMERCIAL",

            fiscal_year=2026,

            fiscal_period=1,

            amount=Decimal("100000"),
        )
    )

    assert len(budget.lines) == 1