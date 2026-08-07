"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : financial_ratio_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 1.2.0
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
            "current_ratio": float(FinancialRatios.current_ratio(
                current_assets=balance_sheet.current_assets,
                current_liabilities=balance_sheet.current_liabilities,
            )),
            "net_margin": float(FinancialRatios.net_margin(
                revenue=income_statement.revenue,
                net_profit=income_statement.net_profit,
            )),
            "gross_margin": float(FinancialRatios.gross_margin(
                revenue=income_statement.revenue,
                gross_profit=income_statement.gross_profit,
            )),
            "operating_margin": float(FinancialRatios.operating_margin(
                revenue=income_statement.revenue,
                operating_profit=income_statement.operating_profit,
            )),
            "inventory_turnover": float(FinancialRatios.inventory_turnover(
                cost_of_goods_sold=income_statement.cost_of_goods_sold,
                average_inventory=balance_sheet.average_inventory,
            )),
            "receivables_turnover": float(FinancialRatios.receivables_turnover(
                revenue=income_statement.revenue,
                average_receivables=balance_sheet.average_receivables,
            )),
            "payables_turnover": float(FinancialRatios.payables_turnover(
                purchases=income_statement.purchases,
                average_payables=balance_sheet.average_payables,
            )),
            "asset_turnover": float(FinancialRatios.asset_turnover(
                revenue=income_statement.revenue,
                average_assets=balance_sheet.average_assets,
            )),
            "inventory_days": float(FinancialRatios.inventory_days(
                cost_of_goods_sold=income_statement.cost_of_goods_sold,
                average_inventory=balance_sheet.average_inventory,
            )),
        }