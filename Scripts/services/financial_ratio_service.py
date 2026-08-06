"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : financial_ratio_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from reporting.balance_sheet import BalanceSheet
from reporting.income_statement import IncomeStatement
from reporting.financial_ratios import FinancialRatios


class FinancialRatioService:

    @staticmethod
    def calculate(
        income_statement: IncomeStatement,
        balance_sheet: BalanceSheet,
    ) -> dict[str, float]:

        return {
            "current_ratio": FinancialRatios.current_ratio(
                current_assets=balance_sheet.assets,
                current_liabilities=balance_sheet.liabilities,
            ),
            "net_margin": FinancialRatios.net_margin(
                revenue=income_statement.revenues,
                net_profit=income_statement.net_profit,
            ),
        }