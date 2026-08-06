import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Scripts')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Scripts.reporting.trial_balance import TrialBalance
from Scripts.reporting.balance_sheet import BalanceSheet
from Scripts.reporting.income_statement import IncomeStatement
from Scripts.repositories.journal_repository import JournalRepository
from tests.helpers.factories import create_sales_invoice, create_purchase_invoice
from Scripts.accounting.general_ledger_engine import GeneralLedgerEngine

from Scripts.services.financial_ratio_service import (
    FinancialRatioService,
)

def test_financial_ratio_service_returns_dictionary():

    repository = JournalRepository()
    repository.save(create_sales_invoice())
    repository.save(create_purchase_invoice())

    ledger = GeneralLedgerEngine()
    for entry in repository.get_all():
        ledger.post(entry)

    tb = TrialBalance.from_ledger(ledger)
    income_statement = IncomeStatement(tb)
    balance_sheet = BalanceSheet(tb)

    ratios = FinancialRatioService.calculate(
        income_statement,
        balance_sheet,
    )

    assert isinstance(ratios, dict)
    assert "current_ratio" in ratios
    assert "net_margin" in ratios