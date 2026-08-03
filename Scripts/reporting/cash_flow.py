"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : cash_flow.py
Object Type     : Cash Flow Engine
Layer           : Reporting
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from __future__ import annotations

from decimal import Decimal

from income_statement import IncomeStatement


class CashFlowStatement:
    """
    Simplified Cash Flow Statement (Indirect Method).
    """

    def __init__(
        self,
        income_statement: IncomeStatement,
        depreciation: Decimal = Decimal("0"),
    ):

        self.pnl = income_statement
        self.depreciation = depreciation

    @property
    def operating_cash_flow(self) -> Decimal:

        return self.pnl.net_profit + self.depreciation

    @property
    def investing_cash_flow(self) -> Decimal:

        return Decimal("0")

    @property
    def financing_cash_flow(self) -> Decimal:

        return Decimal("0")

    @property
    def net_cash_flow(self) -> Decimal:

        return (
            self.operating_cash_flow
            + self.investing_cash_flow
            + self.financing_cash_flow
        )