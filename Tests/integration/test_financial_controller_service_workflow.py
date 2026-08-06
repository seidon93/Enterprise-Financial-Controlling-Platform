import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Scripts')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.helpers.factories import (
    create_sales_invoice,
    create_purchase_invoice,
    create_payroll_journal,
)

from Scripts.repositories.journal_repository import JournalRepository

from Scripts.accounting.general_ledger_engine import GeneralLedgerEngine

from Scripts.services.financial_controller_service import (
    FinancialControllerService,
)

from Scripts.reporting.trial_balance import TrialBalance
from Scripts.reporting.income_statement import IncomeStatement
from Scripts.reporting.balance_sheet import BalanceSheet


def test_financial_controller_service_workflow():

    repository = JournalRepository()

    repository.save(create_sales_invoice())
    repository.save(create_purchase_invoice())
    repository.save(create_payroll_journal())

    ledger = GeneralLedgerEngine()
    for entry in repository.get_all():
        ledger.post(entry)
        
    report = FinancialControllerService.create_report(
        general_ledger=ledger
    )

    assert report.trial_balance.total_debit == report.trial_balance.total_credit
    assert report.income_statement is not None
    assert report.balance_sheet is not None