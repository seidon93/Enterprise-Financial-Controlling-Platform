from decimal import Decimal

from Scripts.reporting.financial_ratios import FinancialRatios


def test_financial_ratios_workflow():

    current_ratio = FinancialRatios.current_ratio(
        current_assets=Decimal("250000"),
        current_liabilities=Decimal("100000"),
    )

    quick_ratio = FinancialRatios.quick_ratio(
        current_assets=Decimal("250000"),
        inventory=Decimal("50000"),
        current_liabilities=Decimal("100000"),
    )

    net_margin = FinancialRatios.net_margin(
        revenue=Decimal("1000000"),
        net_profit=Decimal("180000"),
    )

    return_on_assets = FinancialRatios.return_on_assets(
        net_profit=Decimal("180000"),
        total_assets=Decimal("2000000"),
    )

    assert current_ratio > 0
    assert quick_ratio > 0
    assert net_margin > 0
    assert return_on_assets > 0