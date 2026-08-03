from decimal import Decimal
from datetime import date

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from Scripts.accounting.models import DocumentInfo, JournalEntry, JournalLine
from Scripts.reporting.trial_balance import TrialBalance
from Scripts.reporting.balance_sheet import BalanceSheet


def test_balance_sheet_balances():

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
            account_number="221",
            company_code="CZ01",
            cost_center_code="1000",
            department_code="FIN",
            currency_code="CZK",
            debit_amount=Decimal("1000"),
            credit_amount=Decimal("0"),
            amount_local=Decimal("1000"),
            description="Cash",
        )
    )

    entry.add_line(
        JournalLine(
            line_number=2,
            account_number="401",
            company_code="CZ01",
            cost_center_code="1000",
            department_code="FIN",
            currency_code="CZK",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("1000"),
            amount_local=Decimal("-1000"),
            description="Equity",
        )
    )

    tb = TrialBalance()

    tb.add_entry(entry)

    bs = BalanceSheet(tb)

    assert bs.assets == Decimal("1000")
    assert bs.liabilities == Decimal("1000")
    assert bs.total_liabilities_equity == Decimal("1000")
    assert bs.is_balanced