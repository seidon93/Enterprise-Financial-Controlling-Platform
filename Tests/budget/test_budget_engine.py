import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from decimal import Decimal

from Scripts.budget.budget_engine import BudgetEngine
from Scripts.budget.budget_line import BudgetLine


def test_total_budget():

    lines = [

        BudgetLine(
            company_code="1000",
            account_number="601",
            cost_center_code="100",
            department_code="FIN",
            fiscal_year=2025,
            fiscal_period=1,
            amount=Decimal("100000"),
        ),

        BudgetLine(
            company_code="1000",
            account_number="602",
            cost_center_code="200",
            department_code="FIN",
            fiscal_year=2025,
            fiscal_period=1,
            amount=Decimal("250000"),
        ),
    ]

    assert BudgetEngine.total_budget(lines) == Decimal("350000")