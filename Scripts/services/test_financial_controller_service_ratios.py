import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from repositories.journal_repository import JournalRepository

from tests.helpers.factories import create_sales_invoice

from accounting.general_ledger_engine import GeneralLedgerEngine

from services.financial_controller_service import (
    FinancialControllerService,
)


def test_financial_controller_report_contains_ratios():

    repository = JournalRepository()

    repository.save(
        create_sales_invoice()
    )

    ledger = GeneralLedgerEngine()
    for entry in repository.get_all():
        ledger.post(entry)

    report = FinancialControllerService.create_report(
        general_ledger=ledger
    )

    assert report.financial_ratios is not None
    assert report.financial_ratios == {}