"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : test_journal_line.py
Object Type     : Unit Tests
Layer           : Tests
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Unit tests for JournalLine.
===============================================================================
"""
from decimal import Decimal
from Scripts.accounting.models import JournalLine

def test_create_journal_line():

    line = JournalLine(

        line_number=1,

        account_number="311",

        company_code="CZ01",

        cost_center_code="1000",

        department_code="FIN",

        currency_code="CZK",

        debit_amount=Decimal("1000"),

        credit_amount=Decimal("0"),

        amount_local=Decimal("1000"),

        description="Test journal line",
    )

    assert line.account_number == "311"
    assert line.debit_amount == Decimal("1000")
    assert line.credit_amount == Decimal("0")
    assert line.currency_code == "CZK"


def test_credit_line():

    line = JournalLine(

        line_number=1,

        account_number="604",

        company_code="CZ01",

        cost_center_code="1000",

        department_code="FIN",

        currency_code="CZK",

        debit_amount=Decimal("0"),

        credit_amount=Decimal("1000"),

        amount_local=Decimal("-1000"),

        description="Credit test line",
    )

    assert line.credit_amount == Decimal("1000")
    assert line.debit_amount == Decimal("0")

def test_zero_amounts():

    line = JournalLine(

        line_number=1,

        account_number="221",

        company_code="CZ01",

        cost_center_code="1000",

        department_code="FIN",

        currency_code="CZK",

        debit_amount=Decimal("0"),

        credit_amount=Decimal("0"),

        amount_local=Decimal("0"),

        description="Zero amounts test",
    )

    assert line.debit_amount == Decimal("0")
    assert line.credit_amount == Decimal("0")