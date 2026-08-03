from decimal import Decimal
from datetime import date

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


from Scripts.accounting.models import DocumentInfo, JournalEntry, JournalLine
from Scripts.reporting.trial_balance import TrialBalance
from Scripts.reporting.income_statement import IncomeStatement
from Scripts.reporting.cash_flow import CashFlowStatement


def test_cash_flow():

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

    cf = CashFlowStatement(
        income_statement=pnl,
        depreciation=Decimal("200"),
    )

    assert cf.operating_cash_flow == Decimal("1200")
    assert cf.net_cash_flow == Decimal("1200")