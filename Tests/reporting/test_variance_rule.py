from Scripts.domain.kpi_type import KPIType
from Scripts.domain.variance_rule import VarianceRule


def test_variance_rule():

    rule = VarianceRule(

        account_number="601",

        kpi_type=KPIType.REVENUE,

        favorable_if_higher=True,
    )

    assert rule.account_number == "601"

    assert rule.kpi_type == KPIType.REVENUE

    assert rule.favorable_if_higher is True


def test_expense_rule():

    rule = VarianceRule(

        account_number="521",

        kpi_type=KPIType.EXPENSE,

        favorable_if_higher=False,
    )

    assert rule.kpi_type == KPIType.EXPENSE

    assert rule.favorable_if_higher is False