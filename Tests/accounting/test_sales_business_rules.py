"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : test_sales_business_rules.py
Object Type     : Business Rule Tests
Layer           : Tests
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Business rules for Sales Invoice scenario.
===============================================================================
"""

from decimal import Decimal


def test_vat_calculation():

    net = Decimal("1000")
    vat = Decimal("21")

    vat_amount = net * vat / Decimal("100")

    assert vat_amount == Decimal("210")


def test_gross_amount():

    net = Decimal("1000")
    vat_amount = Decimal("210")

    gross = net + vat_amount

    assert gross == Decimal("1210")


def test_zero_vat():

    net = Decimal("500")

    vat = Decimal("0")

    gross = net + (net * vat / Decimal("100"))

    assert gross == Decimal("500")


def test_positive_invoice_amount():

    amount = Decimal("1500")

    assert amount > 0


def test_due_date_after_invoice():

    from datetime import date

    invoice_date = date(2024, 1, 15)

    due_date = date(2024, 2, 15)

    assert due_date > invoice_date

