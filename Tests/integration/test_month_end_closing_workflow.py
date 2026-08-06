from tests.helpers.factories import (
    create_sales_invoice,
    create_purchase_invoice,
    create_payroll_journal,
    create_inventory_issue,
    create_asset_purchase,
    create_bank_payment,
)

from Scripts.repositories.journal_repository import JournalRepository

from Scripts.accounting.general_ledger_engine import GeneralLedgerEngine

from Scripts.reporting.trial_balance import TrialBalance


def test_month_end_closing_workflow():

    repository = JournalRepository()

    repository.save(create_sales_invoice())
    repository.save(create_purchase_invoice())
    repository.save(create_payroll_journal())
    repository.save(create_inventory_issue())
    repository.save(create_asset_purchase())
    repository.save(create_bank_payment())

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