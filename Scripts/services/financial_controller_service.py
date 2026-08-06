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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from accounting.general_ledger_engine import GeneralLedgerEngine

from reporting.trial_balance import TrialBalance
from reporting.income_statement import IncomeStatement
from reporting.balance_sheet import BalanceSheet

from services.financial_controller_report import (
    FinancialControllerReport,
)


class FinancialControllerService:

    @staticmethod
    def create_report(
        general_ledger: GeneralLedgerEngine,
    ) -> FinancialControllerReport:

        return FinancialControllerReport(
            trial_balance=TrialBalance.from_ledger(
                general_ledger
            ),
            income_statement=IncomeStatement.from_ledger(
                general_ledger
            ),
            balance_sheet=BalanceSheet.from_ledger(
                general_ledger
            ),
            financial_ratios={},
        )