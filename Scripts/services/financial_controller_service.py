"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : financial_controller_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 1.1.0
Status          : Development
===============================================================================
"""

from accounting.general_ledger_engine import GeneralLedgerEngine

from accounting.general_ledger_engine import GeneralLedgerEngine

from reporting.trial_balance import TrialBalance
from reporting.income_statement import IncomeStatement
from reporting.balance_sheet import BalanceSheet

from services.financial_controller_report import (
    FinancialControllerReport,
)
from services.financial_ratio_service import (
    FinancialRatioService,
)


class FinancialControllerService:

    @staticmethod
    def create_report(
        general_ledger: GeneralLedgerEngine,
    ) -> FinancialControllerReport:

        trial_balance = TrialBalance.from_ledger(
            general_ledger
        )

        income_statement = IncomeStatement.from_ledger(
            general_ledger
        )

        balance_sheet = BalanceSheet.from_ledger(
            general_ledger
        )

        financial_ratios = FinancialRatioService.calculate(
            income_statement=income_statement,
            balance_sheet=balance_sheet,
        )

        return FinancialControllerReport(
            trial_balance=trial_balance,
            income_statement=income_statement,
            balance_sheet=balance_sheet,
            financial_ratios=financial_ratios,
        )