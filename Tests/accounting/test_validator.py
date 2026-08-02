"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : test_validator.py
Object Type     : Unit Tests
Layer           : Tests
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Unit tests for JournalEntryValidator.
===============================================================================
"""

from datetime import date
from decimal import Decimal

import pytest

from Scripts.accounting.models import (
    DocumentInfo,
    JournalEntry,
    JournalLine,
)

from Scripts.accounting.validator import (
    JournalEntryValidator,
    ValidationError,
)

def create_document() -> DocumentInfo:

    return DocumentInfo(

        document_number="TEST-000001",

        document_type="TEST",

        posting_date=date(2024, 1, 1),

        document_date=date(2024, 1, 1),

        due_date=date(2024, 1, 31),

        fiscal_year=2024,

        fiscal_period=1,
    )


def debit_line() -> JournalLine:

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


def credit_line() -> JournalLine:

    return JournalLine(

        line_number=2,

        account_number="604",

        company_code="CZ01",

        cost_center_code="1000",

        department_code="FIN",

        currency_code="CZK",

        debit_amount=Decimal("0"),

        credit_amount=Decimal("1000"),

        amount_local=Decimal("1000"),

        description="Credit",
    )

def test_valid_entry():

    entry = JournalEntry(
        document=create_document(),
    )

    entry.add_line(debit_line())
    entry.add_line(credit_line())

    JournalEntryValidator.validate(entry)

def test_requires_two_lines():

    entry = JournalEntry(
        document=create_document(),
    )

    entry.add_line(debit_line())

    with pytest.raises(ValidationError):

        JournalEntryValidator.validate(entry)

def test_unbalanced_entry():

    entry = JournalEntry(
        document=create_document(),
    )

    line = debit_line()

    line.debit_amount = Decimal("2000")

    entry.add_line(line)

    entry.add_line(credit_line())

    with pytest.raises(ValidationError):

        JournalEntryValidator.validate(entry)

def test_missing_account():

    entry = JournalEntry(
        document=create_document(),
    )

    line = debit_line()

    line.account_number = ""

    entry.add_line(line)

    entry.add_line(credit_line())

    with pytest.raises(ValidationError):

        JournalEntryValidator.validate(entry)

def test_missing_company():

    entry = JournalEntry(
        document=create_document(),
    )

    line = debit_line()

    line.company_code = ""

    entry.add_line(line)

    entry.add_line(credit_line())

    with pytest.raises(ValidationError):

        JournalEntryValidator.validate(entry)

def test_missing_currency():

    entry = JournalEntry(
        document=create_document(),
    )

    line = debit_line()

    line.currency_code = ""

    entry.add_line(line)

    entry.add_line(credit_line())

    with pytest.raises(ValidationError):

        JournalEntryValidator.validate(entry)

def test_negative_debit():

    entry = JournalEntry(
        document=create_document(),
    )

    line = debit_line()

    line.debit_amount = Decimal("-1")

    entry.add_line(line)

    entry.add_line(credit_line())

    with pytest.raises(ValidationError):

        JournalEntryValidator.validate(entry)

def test_negative_credit():

    entry = JournalEntry(
        document=create_document(),
    )

    line = credit_line()

    line.credit_amount = Decimal("-1")

    entry.add_line(debit_line())

    entry.add_line(line)

    with pytest.raises(ValidationError):

        JournalEntryValidator.validate(entry)

def test_negative_local_amount():

    entry = JournalEntry(
        document=create_document(),
    )

    line = debit_line()

    line.amount_local = Decimal("-1")

    entry.add_line(line)

    entry.add_line(credit_line())

    with pytest.raises(ValidationError):

        JournalEntryValidator.validate(entry)