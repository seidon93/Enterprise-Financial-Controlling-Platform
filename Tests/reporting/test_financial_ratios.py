"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : test_financial_ratios.py
Object Type     : Unit Tests
Layer           : Reporting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Unit tests for FinancialRatios.
===============================================================================
"""

from decimal import Decimal

from Scripts.reporting.financial_ratios import FinancialRatios


def test_current_ratio():

    ratio = FinancialRatios.current_ratio(
        Decimal("200000"),
        Decimal("100000"),
    )

    assert ratio == Decimal("2")


def test_quick_ratio():

    ratio = FinancialRatios.quick_ratio(
        Decimal("200000"),
        Decimal("50000"),
        Decimal("100000"),
    )

    assert ratio == Decimal("1.5")


def test_cash_ratio():

    ratio = FinancialRatios.cash_ratio(
        Decimal("40000"),
        Decimal("100000"),
    )

    assert ratio == Decimal("0.4")


def test_working_capital():

    wc = FinancialRatios.working_capital(
        Decimal("300000"),
        Decimal("180000"),
    )

    assert wc == Decimal("120000")


def test_working_capital_ratio():

    ratio = FinancialRatios.working_capital_ratio(
        Decimal("300000"),
        Decimal("150000"),
    )

    assert ratio == Decimal("2")