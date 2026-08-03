"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : financial_ratios.py
Object Type     : Financial KPI Engine
Layer           : Reporting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Calculates standard financial KPIs.
===============================================================================
"""

from __future__ import annotations

from decimal import Decimal


class FinancialRatios:
    """Collection of financial KPI calculations."""

    @staticmethod
    def current_ratio(
        current_assets: Decimal,
        current_liabilities: Decimal,
    ) -> Decimal:
        """Current Assets / Current Liabilities"""

        if current_liabilities == Decimal("0"):
            raise ZeroDivisionError(
                "Current liabilities cannot be zero."
            )

        return current_assets / current_liabilities

    @staticmethod
    def quick_ratio(
        current_assets: Decimal,
        inventory: Decimal,
        current_liabilities: Decimal,
    ) -> Decimal:
        """(Current Assets - Inventory) / Current Liabilities"""

        if current_liabilities == Decimal("0"):
            raise ZeroDivisionError(
                "Current liabilities cannot be zero."
            )

        return (current_assets - inventory) / current_liabilities

    @staticmethod
    def cash_ratio(
        cash: Decimal,
        current_liabilities: Decimal,
    ) -> Decimal:
        """Cash / Current Liabilities"""

        if current_liabilities == Decimal("0"):
            raise ZeroDivisionError(
                "Current liabilities cannot be zero."
            )

        return cash / current_liabilities

    @staticmethod
    def working_capital(
        current_assets: Decimal,
        current_liabilities: Decimal,
    ) -> Decimal:
        """Current Assets - Current Liabilities"""

        return current_assets - current_liabilities

    @staticmethod
    def working_capital_ratio(
        current_assets: Decimal,
        current_liabilities: Decimal,
    ) -> Decimal:
        """Current Assets / Current Liabilities"""

        if current_liabilities == Decimal("0"):
            raise ZeroDivisionError(
                "Current liabilities cannot be zero."
            )

        return current_assets / current_liabilities

    @staticmethod
    def gross_margin(
        revenue: Decimal,
        gross_profit: Decimal,
    ) -> Decimal:
        """Gross Profit / Revenue"""

        if revenue == Decimal("0"):
            raise ZeroDivisionError("Revenue cannot be zero.")

        return gross_profit / revenue

    @staticmethod
    def operating_margin(
        revenue: Decimal,
        operating_profit: Decimal,
    ) -> Decimal:
        """Operating Profit / Revenue"""

        if revenue == Decimal("0"):
            raise ZeroDivisionError("Revenue cannot be zero.")

        return operating_profit / revenue

    @staticmethod
    def net_margin(
        revenue: Decimal,
        net_profit: Decimal,
    ) -> Decimal:
        """Net Profit / Revenue"""

        if revenue == Decimal("0"):
            raise ZeroDivisionError("Revenue cannot be zero.")

        return net_profit / revenue

    @staticmethod
    def return_on_assets(
        net_profit: Decimal,
        total_assets: Decimal,
    ) -> Decimal:
        """Return on Assets (ROA)"""

        if total_assets == Decimal("0"):
            raise ZeroDivisionError("Total assets cannot be zero.")

        return net_profit / total_assets

    @staticmethod
    def return_on_equity(
        net_profit: Decimal,
        equity: Decimal,
    ) -> Decimal:
        """Return on Equity (ROE)"""

        if equity == Decimal("0"):
            raise ZeroDivisionError("Equity cannot be zero.")

        return net_profit / equity

    @staticmethod
    def inventory_turnover(
        cost_of_goods_sold: Decimal,
        average_inventory: Decimal,
    ) -> Decimal:
        """
        Inventory Turnover = COGS / Average Inventory
        """

        if average_inventory == Decimal("0"):
            raise ZeroDivisionError("Average inventory cannot be zero.")

        return cost_of_goods_sold / average_inventory

    @staticmethod
    def receivables_turnover(
        revenue: Decimal,
        average_receivables: Decimal,
    ) -> Decimal:
        """
        Receivables Turnover = Revenue / Average Receivables
        """

        if average_receivables == Decimal("0"):
            raise ZeroDivisionError("Average receivables cannot be zero.")

        return revenue / average_receivables

    @staticmethod
    def payables_turnover(
        purchases: Decimal,
        average_payables: Decimal,
    ) -> Decimal:
        """
        Payables Turnover = Purchases / Average Payables
        """

        if average_payables == Decimal("0"):
            raise ZeroDivisionError("Average payables cannot be zero.")

        return purchases / average_payables

    @staticmethod
    def asset_turnover(
        revenue: Decimal,
        average_assets: Decimal,
    ) -> Decimal:
        """
        Asset Turnover = Revenue / Average Assets
        """

        if average_assets == Decimal("0"):
            raise ZeroDivisionError("Average assets cannot be zero.")

        return revenue / average_assets

    @staticmethod
    def inventory_days(
        cost_of_goods_sold: Decimal,
        average_inventory: Decimal,
    ) -> Decimal:
        """
        Days Inventory Outstanding (DIO)
        """

        turnover = FinancialRatios.inventory_turnover(
            cost_of_goods_sold,
            average_inventory,
        )

        return Decimal("365") / turnover