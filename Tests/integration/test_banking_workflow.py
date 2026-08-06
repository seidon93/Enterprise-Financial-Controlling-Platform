from tests.helpers.factories import create_bank_payment

from Scripts.repositories.journal_repository import JournalRepository

from Scripts.accounting.general_ledger_engine import GeneralLedgerEngine

from Scripts.reporting.trial_balance import TrialBalance


def test_bank_payment_to_trial_balance():

    repository = JournalRepository()

    journal = create_bank_payment()

    repository.save(journal)

    ledger = GeneralLedgerEngine()
    for entry in repository.get_all():
        ledger.post(entry)

    trial_balance = TrialBalance.from_ledger(
        ledger
    )

    assert (
        trial_balance.total_debit
        ==
        trial_balance.total_credit
    )