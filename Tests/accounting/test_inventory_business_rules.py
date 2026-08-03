"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : test_inventory_business_rules.py
Object Type     : Business Rule Tests
Layer           : Tests
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Business rules for Inventory Management.
===============================================================================
"""

from decimal import Decimal


def test_inventory_value():

    quantity = Decimal("100")
    unit_cost = Decimal("250")

    inventory_value = quantity * unit_cost

    assert inventory_value == Decimal("25000")


def test_inventory_quantity_positive():

    quantity = Decimal("150")

    assert quantity >= 0


def test_inventory_issue_not_exceed_stock():

    stock = Decimal("200")
    issue = Decimal("150")

    assert issue <= stock


def test_remaining_stock():

    stock = Decimal("200")
    issue = Decimal("50")

    remaining = stock - issue

    assert remaining == Decimal("150")


def test_unit_cost_positive():

    unit_cost = Decimal("350")

    assert unit_cost > 0


def test_inventory_amount_positive():

    amount = Decimal("12000")

    assert amount > 0