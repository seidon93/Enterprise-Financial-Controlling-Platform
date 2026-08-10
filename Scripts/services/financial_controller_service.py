"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : financial_controller_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 3.0.0
Status          : Development

Description:
    Creates the aggregated Financial Controller Report.

    The service combines:
        - Trial Balance
        - Income Statement
        - Balance Sheet
        - Financial Ratios
        - Sales Analysis
        - Price × Volume Analysis
        - Budget vs Actual analysis
        - Year-over-Year analysis
        - Cost variance analysis

    Price × Volume baseline values are derived from actual General Ledger
    sales data through PriceVolumeDataService.
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

from services.sales_analysis_service import (
    SalesAnalysisService,
)

from services.price_volume_data_service import (
    PriceVolumeDataService,
)


class FinancialControllerService:

    @staticmethod
    def create_report(
        general_ledger: GeneralLedgerEngine,
    ) -> FinancialControllerReport:

        # ------------------------------------------------------------------
        # Financial statements
        # ------------------------------------------------------------------

        trial_balance = TrialBalance.from_ledger(
            general_ledger
        )

        income_statement = IncomeStatement.from_ledger(
            general_ledger
        )

        balance_sheet = BalanceSheet.from_ledger(
            general_ledger
        )

        # ------------------------------------------------------------------
        # Financial ratios
        # ------------------------------------------------------------------

        financial_ratios = FinancialRatioService.calculate(
            income_statement=income_statement,
            balance_sheet=balance_sheet,
        )

        # ------------------------------------------------------------------
        # Sales analysis
        # ------------------------------------------------------------------

        sales_analysis = SalesAnalysisService.calculate(
            general_ledger=general_ledger,
        )

        # ------------------------------------------------------------------
        # Price × Volume analysis
        #
        # The comparison is based on actual sales data available in the
        # General Ledger.
        #
        # PriceVolumeDataService determines the two latest available
        # fiscal years automatically.
        # ------------------------------------------------------------------

        try:
            price_volume_data = (
                PriceVolumeDataService.prepare_comparison_data(
                    general_ledger=general_ledger,
                )
            )
        except ValueError:
            price_volume_data = []

        if price_volume_data:

            previous_volume = sum(
                float(item["previous_volume"])
                for item in price_volume_data
            )

            current_volume = sum(
                float(item["current_volume"])
                for item in price_volume_data
            )

            previous_revenue = sum(
                float(item["previous_price"])
                * float(item["previous_volume"])
                for item in price_volume_data
            )

            current_revenue = sum(
                float(item["current_price"])
                * float(item["current_volume"])
                for item in price_volume_data
            )

            if previous_volume != 0:
                previous_price = (
                    previous_revenue
                    / previous_volume
                )
            else:
                previous_price = 0.0

            if current_volume != 0:
                current_price = (
                    current_revenue
                    / current_volume
                )
            else:
                current_price = 0.0

        else:

            previous_price = 0.0
            current_price = sales_analysis["average_price"]

            previous_volume = 0.0
            current_volume = sales_analysis["volume"]

            previous_revenue = 0.0
            current_revenue = sales_analysis["revenue"]

        # ------------------------------------------------------------------
        # Controller planning / comparison inputs
        #
        # These values represent the management-controller baseline used
        # for the demo scenario.
        #
        # Budget and standard-cost values remain explicit controller
        # assumptions. Price × Volume values, however, come from actual
        # transactional sales data.
        # ------------------------------------------------------------------

        revenue_budget = 47_000.0
        expense_budget = 19_000.0

        revenue_previous_year = previous_revenue

        net_profit_previous_year = 25_000.0

        standard_cost = 18_500.0
        actual_cost = 20_000.0

        # ------------------------------------------------------------------
        # Final controller report
        # ------------------------------------------------------------------

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

