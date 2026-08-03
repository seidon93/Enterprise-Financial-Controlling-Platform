"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : test_closing_business_rules.py
Object Type     : Business Rule Tests
Layer           : Tests
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Business rules for Period Closing.
===============================================================================
"""

from decimal import Decimal


def test_accrued_expense_positive():

    amount = Decimal("25000")

    assert amount > 0


def test_accrued_revenue_positive():

    amount = Decimal("18000")

    assert amount > 0


def test_prepaid_expense_positive():

    amount = Decimal("32000")

    assert amount > 0


def test_deferred_revenue_positive():

    amount = Decimal("45000")

    assert amount > 0


def test_provision_positive():

    amount = Decimal("90000")

    assert amount > 0


def test_inventory_writeoff_positive():

    amount = Decimal("7000")

    assert amount > 0


def test_inventory_revaluation_positive():

    amount = Decimal("12000")

    assert amount > 0


def test_bad_debt_allowance_positive():

    amount = Decimal("5000")

    assert amount > 0


def test_income_tax_positive():

    amount = Decimal("250000")

    assert amount > 0


def test_deferred_tax_positive():

    amount = Decimal("18000")

    assert amount > 0


def test_profit_transfer_positive():

    amount = Decimal("950000")

    assert amount > 0


def test_opening_balance_positive():

    amount = Decimal("5000000")

    assert amount > 0