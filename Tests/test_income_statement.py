from decimal import Decimal
from datetime import date

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from Scripts.accounting.models import DocumentInfo, JournalEntry, JournalLine

from Scripts.reporting.trial_balance import TrialBalance
from Scripts.reporting.income_statement import IncomeStatement


def test_income_statement():

    document = DocumentInfo(
        document_number="JV-1",
        document_type="JV",
        posting_date=date(2024, 1, 1),
        document_date=date(2024, 1, 1),
        due_date=date(2024, 1, 1),
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
            description="Receivable",
        )
    )

    entry.add_line(
        JournalLine(
            line_number=2,
            account_number="601",
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

    pnl = IncomeStatement(tb)

    assert pnl.revenues == Decimal("1000")
    assert pnl.expenses == Decimal("0")
    assert pnl.operating_profit == Decimal("1000")
    assert pnl.net_profit == Decimal("1000")