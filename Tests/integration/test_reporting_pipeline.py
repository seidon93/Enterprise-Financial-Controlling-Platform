from tests.helpers.factories import (
    create_sales_invoice,
    create_purchase_invoice,
)

from Scripts.repositories.journal_repository import JournalRepository

from Scripts.accounting.general_ledger_engine import GeneralLedgerEngine

from Scripts.reporting.trial_balance import TrialBalance
from Scripts.reporting.income_statement import IncomeStatement
from Scripts.reporting.balance_sheet import BalanceSheet
from Scripts.reporting.financial_ratios import FinancialRatios


def test_reporting_pipeline():

    from datetime import date
    from decimal import Decimal
    from Scripts.accounting.models import DocumentInfo, JournalEntry, JournalLine

    repository = JournalRepository()

    repository.save(create_sales_invoice())
    repository.save(create_purchase_invoice())

    # Add cash so we have current assets > 0
    cash_entry = JournalEntry(DocumentInfo(
        document_number="CASH-1", document_type="JV",
        posting_date=date(2026, 1, 1), document_date=date(2026, 1, 1),
        due_date=date(2026, 1, 1), fiscal_year=2026, fiscal_period=1
    ))
    cash_entry.add_line(JournalLine(1, "221", "1000", "100", "D01", "CZK", Decimal("500000"), Decimal("0"), Decimal("500000"), "Cash"))
    cash_entry.add_line(JournalLine(2, "901", "1000", "100", "D01", "CZK", Decimal("0"), Decimal("500000"), Decimal("-500000"), "Equity"))
    repository.save(cash_entry)

    ledger = GeneralLedgerEngine()
    for entry in repository.get_all():
        ledger.post(entry)

    trial_balance = TrialBalance.from_ledger(
        ledger
    )

    income_statement = IncomeStatement.from_ledger(
        ledger
    )

    balance_sheet = BalanceSheet.from_ledger(
        ledger
    )

    current_ratio = FinancialRatios.current_ratio(
        current_assets=balance_sheet.assets,
        current_liabilities=balance_sheet.liabilities,
    )

    assert (
        trial_balance.total_debit
        ==
        trial_balance.total_credit
    )

    assert income_statement is not None

    assert balance_sheet is not None

    assert current_ratio > 0