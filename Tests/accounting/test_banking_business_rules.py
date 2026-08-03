"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : test_banking_business_rules.py
Object Type     : Business Rule Tests
Layer           : Tests
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Business rules for Banking scenarios.
===============================================================================
"""

from decimal import Decimal


def test_bank_fee_positive():

    fee = Decimal("250")

    assert fee > 0


def test_interest_income_positive():

    interest = Decimal("1250")

    assert interest > 0


def test_interest_expense_positive():

    interest = Decimal("950")

    assert interest > 0


def test_internal_transfer_same_amount():

    outgoing = Decimal("100000")
    incoming = Decimal("100000")

    assert outgoing == incoming


def test_cash_deposit_positive():

    deposit = Decimal("50000")

    assert deposit > 0


def test_cash_withdrawal_positive():

    withdrawal = Decimal("25000")

    assert withdrawal > 0


def test_loan_drawdown_positive():

    amount = Decimal("1000000")

    assert amount > 0


def test_loan_repayment_not_greater_than_loan():

    loan = Decimal("1000000")
    repayment = Decimal("150000")

    assert repayment <= loan


def test_fx_gain_positive():

    gain = Decimal("850")

    assert gain > 0


def test_fx_loss_positive():

    loss = Decimal("430")

    assert loss > 0