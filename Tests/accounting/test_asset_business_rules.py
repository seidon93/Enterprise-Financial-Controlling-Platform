"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : test_asset_business_rules.py
Object Type     : Business Rule Tests
Layer           : Tests
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Business rules for Fixed Assets.
===============================================================================
"""

from decimal import Decimal


def test_monthly_depreciation():

    acquisition_cost = Decimal("120000")
    useful_life = 60

    monthly = acquisition_cost / useful_life

    assert monthly == Decimal("2000")


def test_book_value_after_one_month():

    acquisition_cost = Decimal("120000")
    monthly = Decimal("2000")

    book_value = acquisition_cost - monthly

    assert book_value == Decimal("118000")


def test_book_value_never_negative():

    acquisition_cost = Decimal("10000")
    accumulated = Decimal("10000")

    book_value = acquisition_cost - accumulated

    assert book_value >= 0


def test_accumulated_depreciation_not_above_cost():

    acquisition_cost = Decimal("50000")
    accumulated = Decimal("45000")

    assert accumulated <= acquisition_cost


def test_useful_life_positive():

    useful_life = 60

    assert useful_life > 0


def test_residual_value_lower_than_cost():

    acquisition_cost = Decimal("100000")
    residual = Decimal("5000")

    assert residual < acquisition_cost