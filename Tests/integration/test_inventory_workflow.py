import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Scripts')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.helpers.factories import create_inventory_issue
from Scripts.repositories.journal_repository import JournalRepository
from Scripts.accounting.general_ledger_engine import GeneralLedgerEngine
from Scripts.reporting.trial_balance import TrialBalance

def test_inventory_issue_to_trial_balance():
    repository = JournalRepository()
    journal = create_inventory_issue()
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