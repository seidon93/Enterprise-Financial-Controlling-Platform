from decimal import Decimal

from Scripts.budget.budget_line import BudgetLine


def test_create_budget_line():

    line = BudgetLine(

        company_code="CZ01",

        account_number="601000",

        cost_center_code="SALES",

        department_code="COMMERCIAL",

        fiscal_year=2026,

        fiscal_period=5,

        amount=Decimal("125000"),
    )

    assert line.company_code == "CZ01"

    assert line.amount == Decimal("125000")