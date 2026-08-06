from datetime import date
from decimal import Decimal

from Scripts.accounting.models import DocumentInfo, JournalEntry, JournalLine

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

def create_purchase_invoice() -> JournalEntry:
    document = DocumentInfo(
        document_number="PI-001",
        document_type="PI",
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
            account_number="501",
            company_code="1000",
            cost_center_code="100",
            department_code="D01",
            currency_code="CZK",
            debit_amount=Decimal("20000"),
            credit_amount=Decimal("0"),
            amount_local=Decimal("20000"),
            description="Expense",
        )
    )
    entry.add_line(
        JournalLine(
            line_number=2,
            account_number="321",
            company_code="1000",
            cost_center_code="100",
            department_code="D01",
            currency_code="CZK",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("20000"),
            amount_local=Decimal("-20000"),
            description="Payable",
        )
    )
    return entry
