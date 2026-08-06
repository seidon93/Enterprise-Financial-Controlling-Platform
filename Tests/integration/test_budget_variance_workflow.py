from decimal import Decimal

from Scripts.budget.budget_line import BudgetLine
from Scripts.reporting.variance_engine import VarianceEngine
from tests.helpers.factories import create_sales_invoice


def test_budget_variance_workflow():

    # Setup Budget Line
    budget_line = BudgetLine(
        account_number="601",
        company_code="1000",
        cost_center_code="100",
        department_code="D01",
        fiscal_year=2026,
        fiscal_period=1,
        amount=Decimal("-100000"), # Revenue is usually a credit
    )

    # Setup Actuals (from factory)
    journal = create_sales_invoice()

    # Compare
    report = VarianceEngine.compare_accounts(
        account_codes=["601"],
        budget_lines=[budget_line],
        journal_entries=[journal],
    )

    assert report is not None
    assert len(report) > 0