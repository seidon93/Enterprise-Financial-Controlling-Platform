from services.controller_dashboard_data import (
    ControllerDashboardData,
)


def test_controller_dashboard_data_creation():

    data = ControllerDashboardData(
        revenue=1000000.0,
        expenses=800000.0,
        net_profit=200000.0,
        current_ratio=2.5,
        quick_ratio=2.0,
        cash_ratio=0.8,
        net_margin=20.0,
        gross_margin=35.0,
        operating_margin=22.0,
        return_on_assets=9.0,
        return_on_equity=20.0,
        inventory_turnover=4.0,
        receivables_turnover=6.0,
        payables_turnover=5.0,
        asset_turnover=0.5,
        inventory_days=91.25,
        working_capital=150000.0,
        working_capital_ratio=1.5,
        revenue_budget=950000.0,
        revenue_variance=50000.0,
        revenue_variance_pct=5.2631578947,
        expense_budget=750000.0,
        expense_variance=50000.0,
        expense_variance_pct=6.6666666667,
        budget_net_profit=200000.0,
        net_profit_variance=0.0,
        net_profit_variance_pct=0.0,
    )

    assert data.revenue == 1000000.0
    assert data.expenses == 800000.0
    assert data.net_profit == 200000.0

    assert data.current_ratio == 2.5
    assert data.quick_ratio == 2.0
    assert data.cash_ratio == 0.8

    assert data.net_margin == 20.0
    assert data.gross_margin == 35.0
    assert data.operating_margin == 22.0

    assert data.return_on_assets == 9.0
    assert data.return_on_equity == 20.0

    assert data.inventory_turnover == 4.0
    assert data.receivables_turnover == 6.0
    assert data.payables_turnover == 5.0
    assert data.asset_turnover == 0.5
    assert data.inventory_days == 91.25

    assert data.working_capital == 150000.0
    assert data.working_capital_ratio == 1.5

    assert data.revenue_budget == 950000.0
    assert data.revenue_variance == 50000.0
    assert data.revenue_variance_pct == 5.2631578947

    assert data.expense_budget == 750000.0
    assert data.expense_variance == 50000.0
    assert data.expense_variance_pct == 6.6666666667

    assert data.budget_net_profit == 200000.0
    assert data.net_profit_variance == 0.0
    assert data.net_profit_variance_pct == 0.0