"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : financial_ratio_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 1.1.0
Status          : Implemented
===============================================================================
"""

from reporting.balance_sheet import BalanceSheet
from reporting.income_statement import IncomeStatement
from reporting.financial_ratios import FinancialRatios


class FinancialRatioService:
    """
    Service responsible for calculating the financial KPI set
    consumed by the Financial Controller reporting layer.
    """

    @staticmethod
    def _safe(func, **kwargs) -> float:
        """Call a ratio function; return 0.0 when the denominator is zero."""
        try:
            return float(func(**kwargs))
        except ZeroDivisionError:
            return 0.0

    @staticmethod
    def calculate(
        income_statement: IncomeStatement,
        balance_sheet: BalanceSheet,
    ) -> dict[str, float]:

        _safe = FinancialRatioService._safe

        return {
            # -----------------------------------------------------------------
            # Liquidity
            # -----------------------------------------------------------------
            "current_ratio": _safe(
                FinancialRatios.current_ratio,
                current_assets=balance_sheet.current_assets,
                current_liabilities=balance_sheet.current_liabilities,
            ),
            "quick_ratio": _safe(
                FinancialRatios.quick_ratio,
                current_assets=balance_sheet.current_assets,
                inventory=balance_sheet.inventory,
                current_liabilities=balance_sheet.current_liabilities,
            ),
            "cash_ratio": _safe(
                FinancialRatios.cash_ratio,
                cash=balance_sheet.cash,
                current_liabilities=balance_sheet.current_liabilities,
            ),

            # -----------------------------------------------------------------
            # Profitability
            # -----------------------------------------------------------------
            "net_margin": _safe(
                FinancialRatios.net_margin,
                revenue=income_statement.revenue,
                net_profit=income_statement.net_profit,
            ),
            "gross_margin": _safe(
                FinancialRatios.gross_margin,
                revenue=income_statement.revenue,
                gross_profit=income_statement.gross_profit,
            ),
            "operating_margin": _safe(
                FinancialRatios.operating_margin,
                revenue=income_statement.revenue,
                operating_profit=income_statement.operating_profit,
            ),
            "return_on_assets": _safe(
                FinancialRatios.return_on_assets,
                net_profit=income_statement.net_profit,
                total_assets=balance_sheet.total_assets,
            ),
            "return_on_equity": _safe(
                FinancialRatios.return_on_equity,
                net_profit=income_statement.net_profit,
                equity=balance_sheet.equity,
            ),

            # -----------------------------------------------------------------
            # Efficiency
            # -----------------------------------------------------------------
            "inventory_turnover": _safe(
                FinancialRatios.inventory_turnover,
                cost_of_goods_sold=income_statement.cost_of_goods_sold,
                average_inventory=balance_sheet.average_inventory,
            ),
            "receivables_turnover": _safe(
                FinancialRatios.receivables_turnover,
                revenue=income_statement.revenue,
                average_receivables=balance_sheet.average_receivables,
            ),
            "payables_turnover": _safe(
                FinancialRatios.payables_turnover,
                purchases=income_statement.purchases,
                average_payables=balance_sheet.average_payables,
            ),
            "asset_turnover": _safe(
                FinancialRatios.asset_turnover,
                revenue=income_statement.revenue,
                average_assets=balance_sheet.average_assets,
            ),
            "inventory_days": _safe(
                FinancialRatios.inventory_days,
                cost_of_goods_sold=income_statement.cost_of_goods_sold,
                average_inventory=balance_sheet.average_inventory,
            ),

            # -----------------------------------------------------------------
            # Working Capital
            # -----------------------------------------------------------------
            "working_capital": _safe(
                FinancialRatios.working_capital,
                current_assets=balance_sheet.current_assets,
                current_liabilities=balance_sheet.current_liabilities,
            ),
            "working_capital_ratio": _safe(
                FinancialRatios.working_capital_ratio,
                current_assets=balance_sheet.current_assets,
                current_liabilities=balance_sheet.current_liabilities,
            ),
        }

