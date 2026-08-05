from datetime import date
from decimal import Decimal

from Scripts.accounting.models import DocumentInfo, JournalEntry, JournalLine
from Scripts.budget.budget_line import BudgetLine
from Scripts.reporting.variance_engine import VarianceEngine


def test_variance_positive():

    result = VarianceEngine.compare(
        budget=Decimal("100000"),
        actual=Decimal("120000"),
    )

    assert result.budget == Decimal("100000")
    assert result.actual == Decimal("120000")
    assert result.variance == Decimal("20000")
    assert result.variance_percent == Decimal("20")


def test_variance_negative():

    result = VarianceEngine.compare(
        budget=Decimal("100000"),
        actual=Decimal("80000"),
    )

    assert result.variance == Decimal("-20000")
    assert result.variance_percent == Decimal("-20")


def test_zero_budget():

    result = VarianceEngine.compare(
        budget=Decimal("0"),
        actual=Decimal("5000"),
    )

    assert result.variance == Decimal("5000")
    assert result.variance_percent == Decimal("0")


def create_sales_invoice() -> JournalEntry:

    document = DocumentInfo(
        document_number="SI-001",
        document_type="SI",
        posting_date=date(2026, 1, 15),
        document_date=date(2026, 1, 15),
        due_date=date(2026, 2, 15),
        fiscal_year=2026,
        fiscal_period=1,
    )

    entry = JournalEntry(document=document)

    entry.add_line(
        JournalLine(
            line_number=1,
            account_number="311",
            company_code="1000",
            cost_center_code="100",
            department_code="D01",
            currency_code="CZK",
            debit_amount=Decimal("50000"),
            credit_amount=Decimal("0"),
            amount_local=Decimal("50000"),
            description="Receivable",
        )
    )

    entry.add_line(
        JournalLine(
            line_number=2,
            account_number="601",
            company_code="1000",
            cost_center_code="100",
            department_code="D01",
            currency_code="CZK",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("50000"),
            amount_local=Decimal("-50000"),
            description="Revenue",
        )
    )

    return entry


def test_compare_account():

    result = VarianceEngine.compare_account(
        account_code="601",
        budget=Decimal("100000"),
        actual=Decimal("120000"),
    )

    assert result.account_code == "601"

    assert result.variance == Decimal("20000")

    assert result.favorable is True

def test_compare_account_unfavorable():

    result = VarianceEngine.compare_account(
        account_code="521",
        budget=Decimal("400000"),
        actual=Decimal("460000"),
    )

    assert result.account_code == "521"

    assert result.variance == Decimal("60000")

    # vyšší mzdové náklady jsou nepříznivé
    assert result.favorable is False

def test_actual_for_account():

    journal = create_sales_invoice()

    actual = VarianceEngine.actual_for_account(
        "601",
        [journal],
    )

    assert actual != Decimal("0")


def test_budget_for_account():

    lines = [

        BudgetLine(
            company_code="1000",
            cost_center_code="100",
            account_number="601",
            department_code="D01",
            fiscal_year=2026,
            fiscal_period=1,
            amount=Decimal("100000"),
        ),

        BudgetLine(
            company_code="1000",
            cost_center_code="100",
            account_number="601",
            department_code="D01",
            fiscal_year=2026,
            fiscal_period=1,
            amount=Decimal("50000"),
        ),
    ]

    assert (
        VarianceEngine.budget_for_account(
            "601",
            lines,
        )
        == Decimal("150000")
    )