from decimal import Decimal

from Scripts.domain.kpi_type import KPIType
from Scripts.domain.variance_rule import VarianceRule
from Scripts.reporting.variance_rules_engine import (
    VarianceRulesEngine,
)


def test_revenue_positive():

    rule = VarianceRule(
        account_number="601",
        kpi_type=KPIType.REVENUE,
        favorable_if_higher=True,
    )

    assert (
        VarianceRulesEngine.is_favorable(
            rule,
            Decimal("100"),
        )
        is True
    )


def test_revenue_negative():

    rule = VarianceRule(
        account_number="601",
        kpi_type=KPIType.REVENUE,
        favorable_if_higher=True,
    )

    assert (
        VarianceRulesEngine.is_favorable(
            rule,
            Decimal("-100"),
        )
        is False
    )


def test_expense_positive():

    rule = VarianceRule(
        account_number="521",
        kpi_type=KPIType.EXPENSE,
        favorable_if_higher=False,
    )

    assert (
        VarianceRulesEngine.is_favorable(
            rule,
            Decimal("100"),
        )
        is False
    )


def test_expense_negative():

    rule = VarianceRule(
        account_number="521",
        kpi_type=KPIType.EXPENSE,
        favorable_if_higher=False,
    )

    assert (
        VarianceRulesEngine.is_favorable(
            rule,
            Decimal("-100"),
        )
        is True
    )