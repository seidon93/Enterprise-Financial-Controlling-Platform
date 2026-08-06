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

from Scripts.accounting.general_ledger_engine import GeneralLedgerEngine
from Scripts.reporting.balance_sheet import BalanceSheet
from Scripts.reporting.income_statement import IncomeStatement
from Scripts.reporting.trial_balance import TrialBalance

from tests.services.financial_controller_report import (
    FinancialControllerReport,
)


class FinancialControllerService:

    @staticmethod
    def create_report(general_ledger: GeneralLedgerEngine) -> FinancialControllerReport:

        return FinancialControllerReport(
            trial_balance=TrialBalance.from_ledger(general_ledger),
            income_statement=IncomeStatement.from_ledger(general_ledger),
            balance_sheet=BalanceSheet.from_ledger(general_ledger),
        )