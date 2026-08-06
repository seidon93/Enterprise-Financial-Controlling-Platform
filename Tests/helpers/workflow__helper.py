import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Scripts')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Scripts.accounting.general_ledger_engine import (
    GeneralLedgerEngine,
)


def build_general_ledger(
    journal_repository,
):

    ledger = GeneralLedgerEngine()
    for e in journal_repository.get_all():
        ledger.post(e)
    return ledger