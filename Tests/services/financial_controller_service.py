"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : financial_controller_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 1.0.0
Status          : Development
===============================================================================
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Scripts')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Scripts.accounting.general_ledger_engine import GeneralLedgerEngine
from Scripts.reporting.balance_sheet import BalanceSheet
from Scripts.reporting.income_statement import IncomeStatement
from Scripts.reporting.trial_balance import TrialBalance

from tests.services.financial_controller_report import (
    FinancialControllerReport,
)


from Scripts.repositories.journal_repository import JournalRepository

from tests.helpers.factories import create_sales_invoice

from Scripts.accounting.general_ledger_engine import GeneralLedgerEngine

from Scripts.services.financial_controller_service import (
    FinancialControllerService,
)


def test_create_financial_controller_report():

    repository = JournalRepository()

    repository.save(create_sales_invoice())

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

    assert report.trial_balance is not None
    assert report.income_statement is not None
    assert report.balance_sheet is not None