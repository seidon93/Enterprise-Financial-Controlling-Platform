from Scripts.budget.budget_line import BudgetLine
from decimal import Decimal
from Scripts.repositories.budget_repository import BudgetRepository

def test_budget_repository():

    repo = BudgetRepository()

    repo.save(
        BudgetLine(
            company_code="1000",
            cost_center_code="100",
            account_number="601",
            department_code="SALES",
            fiscal_year=2024,
            fiscal_period=1,
            amount=Decimal("100")
        )
    )

    assert repo.count() == 1