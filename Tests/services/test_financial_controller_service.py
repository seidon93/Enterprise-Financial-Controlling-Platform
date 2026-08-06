import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Scripts')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Scripts.repositories.journal_repository import JournalRepository

from tests.helpers.factories import create_sales_invoice, create_purchase_invoice

from Scripts.accounting.general_ledger_engine import GeneralLedgerEngine

from Scripts.services.financial_controller_service import (
    FinancialControllerService,
)

def test_create_financial_controller_report():

    repository = JournalRepository()

    repository.save(create_sales_invoice())
    repository.save(create_purchase_invoice())

    ledger = GeneralLedgerEngine()
    for entry in repository.get_all():
        ledger.post(entry)

    report = FinancialControllerService.create_report(
        ledger
    )

    assert report.trial_balance is not None
    assert report.income_statement is not None
    assert report.balance_sheet is not None
    assert isinstance(report.financial_ratios, dict)