from datetime import date
from decimal import Decimal

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from Scripts.accounting.models import JournalEntry

from Scripts.accounting.general_ledger_engine import GeneralLedgerEngine
from Scripts.accounting.models import (
    DocumentInfo,
    JournalEntry,
    JournalLine,
)


def build_entry():

    document = DocumentInfo(
        document_number="JV-2024-000001",
        document_type="JV",
        posting_date=date(2024, 1, 1),
        document_date=date(2024, 1, 1),
        due_date=date(2024, 1, 31),
        fiscal_year=2024,
        fiscal_period=1,
    )

    entry = JournalEntry(document=document)

    entry.add_line(
        JournalLine(
            line_number=1,
            account_number="111000",
            company_code="CZ01",
            cost_center_code="100",
            department_code="FIN",
            currency_code="CZK",
            debit_amount=Decimal("100"),
            credit_amount=Decimal("0"),
            amount_local=Decimal("100"),
            description="Debit",
        )
    )

    entry.add_line(
        JournalLine(
            line_number=2,
            account_number="602000",
            company_code="CZ01",
            cost_center_code="100",
            department_code="FIN",
            currency_code="CZK",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("100"),
            amount_local=Decimal("100"),
            description="Credit",
        )
    )

    return entry


def test_post_entry():

    ledger = GeneralLedgerEngine()

    ledger.post(build_entry())

    assert ledger.number_of_entries == 1


def test_entries_property():

    ledger = GeneralLedgerEngine()

    ledger.post(build_entry())

    assert len(ledger.entries) == 1