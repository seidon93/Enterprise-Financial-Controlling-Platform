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