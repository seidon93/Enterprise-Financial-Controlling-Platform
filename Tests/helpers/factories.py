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

def create_payroll_journal() -> JournalEntry:
    document = DocumentInfo(
        document_number="PAY-001",
        document_type="PY",
        posting_date=date(2026, 1, 31),
        document_date=date(2026, 1, 31),
        due_date=date(2026, 2, 10),
        fiscal_year=2026,
        fiscal_period=1,
    )
    entry = JournalEntry(document=document)
    entry.add_line(
        JournalLine(
            line_number=1,
            account_number="521",
            company_code="1000",
            cost_center_code="100",
            department_code="D01",
            currency_code="CZK",
            debit_amount=Decimal("100000"),
            credit_amount=Decimal("0"),
            amount_local=Decimal("100000"),
            description="Salary Expense",
        )
    )
    entry.add_line(
        JournalLine(
            line_number=2,
            account_number="331",
            company_code="1000",
            cost_center_code="100",
            department_code="D01",
            currency_code="CZK",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("70000"),
            amount_local=Decimal("-70000"),
            description="Wages Payable",
        )
    )
    entry.add_line(
        JournalLine(
            line_number=3,
            account_number="342",
            company_code="1000",
            cost_center_code="100",
            department_code="D01",
            currency_code="CZK",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("15000"),
            amount_local=Decimal("-15000"),
            description="Income Tax Withheld",
        )
    )
    entry.add_line(
        JournalLine(
            line_number=4,
            account_number="336",
            company_code="1000",
            cost_center_code="100",
            department_code="D01",
            currency_code="CZK",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("15000"),
            amount_local=Decimal("-15000"),
            description="Social/Health Insurance",
        )
    )
    return entry

def create_inventory_issue() -> JournalEntry:
    document = DocumentInfo(
        document_number="INV-001",
        document_type="GI",
        posting_date=date(2026, 1, 15),
        document_date=date(2026, 1, 15),
        due_date=date(2026, 1, 15),
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
            debit_amount=Decimal("5000"),
            credit_amount=Decimal("0"),
            amount_local=Decimal("5000"),
            description="Material Consumption",
        )
    )
    entry.add_line(
        JournalLine(
            line_number=2,
            account_number="112",
            company_code="1000",
            cost_center_code="100",
            department_code="D01",
            currency_code="CZK",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("5000"),
            amount_local=Decimal("-5000"),
            description="Inventory Credit",
        )
    )
    return entry
