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

def test_budget_by_account():

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
            account_number="601",
            cost_center_code="100",
            department_code="FIN",
            fiscal_year=2025,
            fiscal_period=2,
            amount=Decimal("50000"),
        ),

        BudgetLine(
            company_code="1000",
            account_number="602",
            cost_center_code="100",
            department_code="FIN",
            fiscal_year=2025,
            fiscal_period=1,
            amount=Decimal("30000"),
        ),
    ]

    result = BudgetEngine.budget_by_account(lines)

    assert result["601"] == Decimal("150000")

    assert result["602"] == Decimal("30000")

def test_budget_by_cost_center():

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
            account_number="601",
            cost_center_code="200",
            department_code="FIN",
            fiscal_year=2025,
            fiscal_period=1,
            amount=Decimal("50000"),
        ),
    ]

    result = BudgetEngine.budget_by_cost_center(lines)

    assert result["100"] == Decimal("100000")

    assert result["200"] == Decimal("50000")

def test_budget_by_company():

    lines = [

        BudgetLine(
            company_code="1000",
            account_number="601",
            cost_center_code="100",
            department_code="FIN",
            fiscal_year=2025,
            fiscal_period=1,
            amount=Decimal("120000"),
        ),

        BudgetLine(
            company_code="2000",
            account_number="601",
            cost_center_code="100",
            department_code="FIN",
            fiscal_year=2025,
            fiscal_period=1,
            amount=Decimal("80000"),
        ),
    ]

    result = BudgetEngine.budget_by_company(lines)

    assert result["1000"] == Decimal("120000")

    assert result["2000"] == Decimal("80000")

def test_budget_by_account():

    lines = [

        BudgetLine(
            company_code="1000",
            cost_center_code="100",
            account_number="601",
            amount=Decimal("100000"),
        ),

        BudgetLine(
            company_code="1000",
            cost_center_code="100",
            account_number="601",
            amount=Decimal("50000"),
        ),

        BudgetLine(
            company_code="1000",
            cost_center_code="100",
            account_number="602",
            amount=Decimal("30000"),
        ),
    ]

    result = BudgetEngine.budget_by_account(lines)

    assert result["601"] == Decimal("150000")

    assert result["602"] == Decimal("30000")

def test_budget_by_cost_center():

    lines = [

        BudgetLine(
            company_code="1000",
            cost_center_code="100",
            account_number="601",
            amount=Decimal("100000"),
        ),

        BudgetLine(
            company_code="1000",
            cost_center_code="200",
            account_number="601",
            amount=Decimal("50000"),
        ),
    ]

    result = BudgetEngine.budget_by_cost_center(lines)

    assert result["100"] == Decimal("100000")

    assert result["200"] == Decimal("50000")

def test_budget_by_company():

    lines = [

        BudgetLine(
            company_code="1000",
            cost_center_code="100",
            account_number="601",
            amount=Decimal("120000"),
        ),

        BudgetLine(
            company_code="2000",
            cost_center_code="100",
            account_number="601",
            amount=Decimal("80000"),
        ),
    ]

    result = BudgetEngine.budget_by_company(lines)

    assert result["1000"] == Decimal("120000")

    assert result["2000"] == Decimal("80000")