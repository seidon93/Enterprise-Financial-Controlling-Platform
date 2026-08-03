"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : test_trial_balance.py
Object Type     : Unit Tests
Layer           : Tests
Version         : 1.0.0
===============================================================================
"""

from decimal import Decimal
from datetime import date
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from Scripts.accounting.models import (
    DocumentInfo,
    JournalEntry,
    JournalLine,
)

from Scripts.reporting.trial_balance import TrialBalance


def test_trial_balance_balanced():

    document = DocumentInfo(
        document_number="JV-2024-000001",
        document_type="JV",
        posting_date=date(2024, 1, 15),
        document_date=date(2024, 1, 15),
        due_date=date(2024, 1, 15),
        fiscal_year=2024,
        fiscal_period=1,
    )

    entry = JournalEntry(document=document)

    entry.add_line(
        JournalLine(
            line_number=1,
            account_number="311",
            company_code="CZ01",
            cost_center_code="1000",
            department_code="FIN",
            currency_code="CZK",
            debit_amount=Decimal("1000"),
            credit_amount=Decimal("0"),
            amount_local=Decimal("1000"),
            description="AR",
        )
    )

    entry.add_line(
        JournalLine(
            line_number=2,
            account_number="604",
            company_code="CZ01",
            cost_center_code="1000",
            department_code="FIN",
            currency_code="CZK",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("1000"),
            amount_local=Decimal("-1000"),
            description="Revenue",
        )
    )

    tb = TrialBalance()

    tb.add_entry(entry)

    assert tb.is_balanced
    assert tb.total_debit == Decimal("1000")
    assert tb.total_credit == Decimal("1000")