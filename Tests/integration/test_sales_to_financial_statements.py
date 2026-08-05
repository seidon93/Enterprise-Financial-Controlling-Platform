from tests.reporting.test_variance_engine import create_sales_invoice
from Scripts.repositories.journal_repository import JournalRepository
from Scripts.accounting.general_ledger_engine import GeneralLedgerEngine
from Scripts.reporting.trial_balance import TrialBalance
from Scripts.reporting.income_statement import IncomeStatement
from Scripts.reporting.balance_sheet import BalanceSheet

def test_sales_invoice_generates_trial_balance():

    journal = create_sales_invoice()

    repo = JournalRepository()

    repo.save(journal)

    ledger = GeneralLedgerEngine()
    for e in repo.get_all():
        ledger.post(e)

    trial_balance = TrialBalance.from_ledger(
        ledger
    )

    assert trial_balance.total_debit == trial_balance.total_credit