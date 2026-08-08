"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : financial_controller_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 2.0.0
Status          : Development
Description     : Creates the aggregated Financial Controller Report.
===============================================================================
"""

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

        # ------------------------------------------------------------------
        # Controller planning / comparison inputs
        #
        # These values represent the management-controller baseline used
        # for the demo scenario. They are intentionally kept in the report
        # layer so that the dashboard services remain data-source agnostic.
        # ------------------------------------------------------------------

        revenue_budget = 47_000.0
        expense_budget = 19_000.0

        revenue_previous_year = 46_000.0
        net_profit_previous_year = 25_000.0

        previous_price = 95.0
        current_price = 100.0

        previous_volume = 485.0
        current_volume = 500.0

        standard_cost = 18_500.0
        actual_cost = 20_000.0

        return FinancialControllerReport(
            trial_balance=trial_balance,
            income_statement=income_statement,
            balance_sheet=balance_sheet,
            financial_ratios=financial_ratios,

            revenue_budget=revenue_budget,
            expense_budget=expense_budget,

            revenue_previous_year=revenue_previous_year,
            net_profit_previous_year=net_profit_previous_year,

            previous_price=previous_price,
            current_price=current_price,

            previous_volume=previous_volume,
            current_volume=current_volume,

            standard_cost=standard_cost,
            actual_cost=actual_cost,
        )

