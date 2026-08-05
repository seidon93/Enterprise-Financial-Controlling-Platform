from Scripts.repositories.journal_repository import JournalRepository
from tests.reporting.test_variance_engine import create_sales_invoice
from Scripts.accounting.general_ledger_engine import GeneralLedgerEngine


def test_sales_invoice_to_general_ledger():

    repo = JournalRepository()

    journal = create_sales_invoice()

    repo.save(journal)

    ledger = GeneralLedgerEngine()
    for e in repo.get_all():
        ledger.post(e)

    assert ledger is not None

from Scripts.reporting.trial_balance import TrialBalance


def test_sales_invoice_to_trial_balance():

    repo = JournalRepository()

    repo.save(create_sales_invoice())

    ledger = GeneralLedgerEngine()
    for e in repo.get_all():
        ledger.post(e)

    tb = TrialBalance.from_ledger(
        ledger
    )

    assert tb.total_debit == tb.total_credit

from Scripts.reporting.income_statement import IncomeStatement


def test_sales_invoice_to_income_statement():

    repo = JournalRepository()

    repo.save(create_sales_invoice())

    ledger = GeneralLedgerEngine()
    for e in repo.get_all():
        ledger.post(e)

    statement = IncomeStatement.from_ledger(
        ledger
    )

    assert statement is not None