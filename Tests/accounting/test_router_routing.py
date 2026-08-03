"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : test_router_routing.py
Object Type     : Router Tests
Layer           : Tests
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Parameterized tests for ScenarioRouter.
===============================================================================
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from Scripts.accounting.scenario_router import ScenarioRouter
from Scripts.domain.business_event import BusinessEvent
from Scripts.domain.business_event_type import BusinessEventType

def create_router():

    kwargs = {

        "sales_scenario": MagicMock(),
        "purchase_scenario": MagicMock(),
        "customer_payment_scenario": MagicMock(),
        "supplier_payment_scenario": MagicMock(),

        "asset_acquisition_scenario": MagicMock(),
        "asset_capitalization_scenario": MagicMock(),
        "asset_depreciation_scenario": MagicMock(),
        "asset_impairment_scenario": MagicMock(),
        "asset_disposal_scenario": MagicMock(),
        "asset_sale_scenario": MagicMock(),
        "asset_transfer_scenario": MagicMock(),

        "inventory_receipt_scenario": MagicMock(),
        "inventory_issue_scenario": MagicMock(),
        "inventory_transfer_scenario": MagicMock(),
        "inventory_adjustment_scenario": MagicMock(),

        "payroll_expense_scenario": MagicMock(),
        "employer_contribution_scenario": MagicMock(),
        "payroll_tax_scenario": MagicMock(),
        "payroll_payment_scenario": MagicMock(),

        "bank_fee_scenario": MagicMock(),
        "interest_income_scenario": MagicMock(),
        "interest_expense_scenario": MagicMock(),
        "fx_gain_scenario": MagicMock(),
        "fx_loss_scenario": MagicMock(),
        "loan_drawdown_scenario": MagicMock(),
        "loan_repayment_scenario": MagicMock(),
        "cash_deposit_scenario": MagicMock(),
        "cash_withdrawal_scenario": MagicMock(),
        "internal_transfer_scenario": MagicMock(),

        "accrued_expense_scenario": MagicMock(),
        "accrued_revenue_scenario": MagicMock(),
        "prepaid_expense_scenario": MagicMock(),
        "deferred_revenue_scenario": MagicMock(),
        "provision_scenario": MagicMock(),
        "inventory_writeoff_scenario": MagicMock(),
        "inventory_revaluation_scenario": MagicMock(),
        "bad_debt_allowance_scenario": MagicMock(),
        "foreign_currency_revaluation_scenario": MagicMock(),
        "income_tax_accrual_scenario": MagicMock(),
        "deferred_tax_scenario": MagicMock(),
        "profit_transfer_scenario": MagicMock(),
        "opening_balance_scenario": MagicMock(),
    }

    return ScenarioRouter(**kwargs), kwargs

@pytest.mark.parametrize(

    "event_type,scenario",

    [

        (BusinessEventType.SALES_INVOICE, "sales_scenario"),

        (BusinessEventType.PURCHASE_INVOICE, "purchase_scenario"),

        (BusinessEventType.CUSTOMER_PAYMENT, "customer_payment_scenario"),

        (BusinessEventType.SUPPLIER_PAYMENT, "supplier_payment_scenario"),

    ]

)

def test_basic_routing(event_type, scenario):

    router, mocks = create_router()

    event = BusinessEvent(

        event_type=event_type,

        company_code="CZ01",

        cost_center_code="1000",

        department_code="FIN",

        currency_code="CZK",

        event_date=date(2024,1,1),

        due_date=date(2024,2,1),

        amount=Decimal("1000"),

        vat_rate=Decimal("21"),

        description="Test",

        customer_code="C001",

        supplier_code="S001",

    )

    router.process(event)

    mocks[scenario].create.assert_called_once()