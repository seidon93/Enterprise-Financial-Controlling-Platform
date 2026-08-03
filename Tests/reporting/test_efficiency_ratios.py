"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : test_efficiency_ratios.py
Object Type     : Unit Tests
Layer           : Reporting
===============================================================================
"""

from decimal import Decimal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from Scripts.reporting.financial_ratios import FinancialRatios


def test_inventory_turnover():

    ratio = FinancialRatios.inventory_turnover(
        cost_of_goods_sold=Decimal("1200000"),
        average_inventory=Decimal("300000"),
    )

    assert ratio == Decimal("4")


def test_receivables_turnover():

    ratio = FinancialRatios.receivables_turnover(
        revenue=Decimal("1800000"),
        average_receivables=Decimal("300000"),
    )

    assert ratio == Decimal("6")


def test_payables_turnover():

    ratio = FinancialRatios.payables_turnover(
        purchases=Decimal("900000"),
        average_payables=Decimal("150000"),
    )

    assert ratio == Decimal("6")


def test_asset_turnover():

    ratio = FinancialRatios.asset_turnover(
        revenue=Decimal("2500000"),
        average_assets=Decimal("5000000"),
    )

    assert ratio == Decimal("0.5")


def test_inventory_days():

    days = FinancialRatios.inventory_days(
        cost_of_goods_sold=Decimal("1200000"),
        average_inventory=Decimal("300000"),
    )

    assert days == Decimal("91.25")