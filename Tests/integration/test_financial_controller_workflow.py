from tests.helpers.factories import (
    create_sales_invoice,
    create_purchase_invoice,
    create_payroll_journal,
)

from Scripts.repositories.journal_repository import JournalRepository

from Scripts.accounting.general_ledger_engine import GeneralLedgerEngine

from Scripts.reporting.trial_balance import TrialBalance
from Scripts.reporting.income_statement import IncomeStatement
from Scripts.reporting.balance_sheet import BalanceSheet


def test_financial_controller_workflow():

    repository = JournalRepository()

    repository.save(create_sales_invoice())
    repository.save(create_purchase_invoice())
    repository.save(create_payroll_journal())

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

    assert (
        trial_balance.total_debit
        ==
        trial_balance.total_credit
    )

    assert income_statement is not None

    assert balance_sheet is not None