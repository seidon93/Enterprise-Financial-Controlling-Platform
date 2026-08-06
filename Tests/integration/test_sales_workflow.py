import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Scripts')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Scripts.repositories.journal_repository import JournalRepository
from tests.helpers.factories import create_sales_invoice
from tests.helpers.workflow__helper import build_general_ledger
from tests.helpers.assertions import assert_trial_balance_balanced
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

def test_sales_invoice_to_trial_balance(
    journal_repository,
    sales_invoice,
):

    journal_repository.save(sales_invoice)

    ledger = build_general_ledger(
        journal_repository
    )

    tb = TrialBalance.from_ledger(
        ledger
    )

    assert_trial_balance_balanced(tb)