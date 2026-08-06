from tests.helpers.factories import create_purchase_invoice
from Scripts.repositories.journal_repository import JournalRepository
from Scripts.accounting.general_ledger_engine import GeneralLedgerEngine
from Scripts.reporting.trial_balance import TrialBalance
from tests.helpers.workflow__helper import build_general_ledger
from tests.helpers.assertions import assert_trial_balance_balanced

def test_purchase_invoice_to_trial_balance():

    repository = JournalRepository()

    journal = create_purchase_invoice()

    repository.save(journal)

    ledger = GeneralLedgerEngine()
    for e in repository.get_all():
        ledger.post(e)

    trial_balance = TrialBalance.from_ledger(
        ledger
    )

    assert (
        trial_balance.total_debit
        ==
        trial_balance.total_credit
    )