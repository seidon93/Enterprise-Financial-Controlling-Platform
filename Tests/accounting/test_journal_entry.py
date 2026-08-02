"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : test_journal_entry.py
Object Type     : Unit Tests
Layer           : Tests
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Unit tests for JournalEntry.
===============================================================================
"""

from datetime import date
from decimal import Decimal

from Scripts.accounting.models import (
    DocumentInfo,
    JournalEntry,
    JournalLine,
)


def create_document() -> DocumentInfo:

    return DocumentInfo(

        document_number="SALES-2024-000001",

        document_type="SALES",

        posting_date=date(2024, 1, 15),

        document_date=date(2024, 1, 15),

        due_date=date(2024, 2, 15),

        fiscal_year=2024,

        fiscal_period=1,
    )


def create_debit_line() -> JournalLine:

    return JournalLine(

        line_number=1,

        account_number="311",

        company_code="CZ01",

        cost_center_code="1000",

        department_code="FIN",

        currency_code="CZK",

        debit_amount=Decimal("1000"),

        credit_amount=Decimal("0"),

        amount_local=Decimal("1000"),

        description="Debit",
    )


def create_credit_line() -> JournalLine:

    return JournalLine(

        line_number=2,

        account_number="604",

        company_code="CZ01",

        cost_center_code="1000",

        department_code="FIN",

        currency_code="CZK",

        debit_amount=Decimal("0"),

        credit_amount=Decimal("1000"),

        amount_local=Decimal("-1000"),

        description="Credit",
    )


def test_create_journal_entry():

    entry = JournalEntry(

        document=create_document(),
    )

    assert entry.document.document_number == "SALES-2024-000001"

    assert len(entry.lines) == 0


def test_add_single_line():

    entry = JournalEntry(

        document=create_document(),
    )

    entry.add_line(

        create_debit_line()
    )

    assert len(entry.lines) == 1


def test_add_two_lines():

    entry = JournalEntry(

        document=create_document(),
    )

    entry.add_line(

        create_debit_line()
    )

    entry.add_line(

        create_credit_line()
    )

    assert len(entry.lines) == 2

def test_total_debit():

    entry = JournalEntry(
        document=create_document(),
    )

    entry.add_line(create_debit_line())
    entry.add_line(create_credit_line())

    assert entry.total_debit == Decimal("1000")

def test_total_credit():

    entry = JournalEntry(
        document=create_document(),
    )

    entry.add_line(create_debit_line())
    entry.add_line(create_credit_line())

    assert entry.total_credit == Decimal("1000")

def test_balanced_entry():

    entry = JournalEntry(
        document=create_document(),
    )

    entry.add_line(create_debit_line())
    entry.add_line(create_credit_line())

    assert entry.is_balanced is True

def test_unbalanced_entry():

    entry = JournalEntry(
        document=create_document(),
    )

    entry.add_line(create_debit_line())

    assert entry.is_balanced is False

def test_empty_journal():

    entry = JournalEntry(
        document=create_document(),
    )

    assert entry.total_debit == Decimal("0")
    assert entry.total_credit == Decimal("0")
    assert entry.is_balanced is True