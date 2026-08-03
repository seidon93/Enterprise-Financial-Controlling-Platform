"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : test_leverage_ratios.py
Object Type     : Unit Tests
Layer           : Reporting
===============================================================================
"""

from decimal import Decimal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from Scripts.reporting.financial_ratios import FinancialRatios


def test_debt_ratio():

    ratio = FinancialRatios.debt_ratio(
        total_liabilities=Decimal("1200000"),
        total_assets=Decimal("3000000"),
    )

    assert ratio == Decimal("0.4")


def test_equity_ratio():

    ratio = FinancialRatios.equity_ratio(
        equity=Decimal("1800000"),
        total_assets=Decimal("3000000"),
    )

    assert ratio == Decimal("0.6")


def test_debt_to_equity():

    ratio = FinancialRatios.debt_to_equity(
        total_liabilities=Decimal("1200000"),
        equity=Decimal("1800000"),
    )

    assert ratio == Decimal("0.6666666666666666666666666667")


def test_interest_coverage():

    ratio = FinancialRatios.interest_coverage(
        operating_profit=Decimal("500000"),
        interest_expense=Decimal("50000"),
    )

    assert ratio == Decimal("10")