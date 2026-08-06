from repositories.journal_repository import JournalRepository

from scenarios.sales import create_sales_invoice

from accounting.general_ledger_engine import GeneralLedgerEngine

from services.financial_controller_service import (
    FinancialControllerService,
)


def test_financial_controller_report_contains_ratios():

    repository = JournalRepository()

    repository.save(
        create_sales_invoice()
    )

    ledger = GeneralLedgerEngine(
        repository.get_all()
    )

    report = FinancialControllerService.create_report(
        ledger
    )

    assert report.financial_ratios == {}