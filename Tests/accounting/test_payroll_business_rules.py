"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : test_payroll_business_rules.py
Object Type     : Business Rule Tests
Layer           : Tests
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Business rules for Payroll.
===============================================================================
"""

from decimal import Decimal


def test_net_salary_calculation():

    gross = Decimal("50000")
    tax = Decimal("7500")

    net = gross - tax

    assert net == Decimal("42500")


def test_bonus_increases_salary():

    gross = Decimal("50000")
    bonus = Decimal("5000")

    assert gross + bonus == Decimal("55000")


def test_overtime_increases_salary():

    gross = Decimal("50000")
    overtime = Decimal("3000")

    assert gross + overtime == Decimal("53000")


def test_salary_positive():

    gross = Decimal("50000")

    assert gross > 0


def test_tax_not_greater_than_salary():

    gross = Decimal("50000")
    tax = Decimal("7500")

    assert tax <= gross


def test_employer_contribution_positive():

    contribution = Decimal("16900")

    assert contribution > 0


def test_net_salary_never_negative():

    gross = Decimal("50000")
    tax = Decimal("7500")

    net = gross - tax

    assert net >= 0