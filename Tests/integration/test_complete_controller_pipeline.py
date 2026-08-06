import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Scripts')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

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

from Scripts.services.financial_controller_service import (
    FinancialControllerService,
)

from Scripts.reporting.trial_balance import TrialBalance
from Scripts.reporting.income_statement import IncomeStatement
from Scripts.reporting.balance_sheet import BalanceSheet


def test_complete_controller_pipeline():

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

    trial_balance = TrialBalance.from_ledger(ledger)
    income_statement = IncomeStatement.from_ledger(ledger)
    balance_sheet = BalanceSheet.from_ledger(ledger)

    report = FinancialControllerService.create_report(
        trial_balance=trial_balance,
        income_statement=income_statement,
        balance_sheet=balance_sheet,
        variances=[]
    )

    assert (
        report.trial_balance.total_debit
        ==
        report.trial_balance.total_credit
    )

    assert report.income_statement is not None

    assert report.balance_sheet is not None