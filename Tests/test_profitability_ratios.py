"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : test_profitability_ratios.py
Object Type     : Unit Tests
Layer           : Reporting
===============================================================================
"""

from decimal import Decimal

from Scripts.reporting.financial_ratios import FinancialRatios


def test_gross_margin():

    ratio = FinancialRatios.gross_margin(
        revenue=Decimal("1000000"),
        gross_profit=Decimal("350000"),
    )

    assert ratio == Decimal("0.35")


def test_operating_margin():

    ratio = FinancialRatios.operating_margin(
        revenue=Decimal("1000000"),
        operating_profit=Decimal("220000"),
    )

    assert ratio == Decimal("0.22")


def test_net_margin():

    ratio = FinancialRatios.net_margin(
        revenue=Decimal("1000000"),
        net_profit=Decimal("170000"),
    )

    assert ratio == Decimal("0.17")


def test_return_on_assets():

    ratio = FinancialRatios.return_on_assets(
        net_profit=Decimal("120000"),
        total_assets=Decimal("2400000"),
    )

    assert ratio == Decimal("0.05")


def test_return_on_equity():

    ratio = FinancialRatios.return_on_equity(
        net_profit=Decimal("180000"),
        equity=Decimal("900000"),
    )

    assert ratio == Decimal("0.20")