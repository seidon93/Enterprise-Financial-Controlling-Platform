from services.controller_dashboard_data import (
    ControllerDashboardData,
)


def test_controller_dashboard_data_creation():

    data = ControllerDashboardData(
        revenue=1000000.0,
        expenses=800000.0,
        net_profit=200000.0,
        current_ratio=2.5,
        net_margin=20.0,
        gross_margin=35.0,
        operating_margin=22.0,
        inventory_turnover=4.0,
        receivables_turnover=6.0,
        payables_turnover=5.0,
        asset_turnover=0.5,
        inventory_days=91.25,
    )

    assert data.revenue == 1000000.0
    assert data.expenses == 800000.0
    assert data.net_profit == 200000.0
    assert data.current_ratio == 2.5
    assert data.net_margin == 20.0
    assert data.gross_margin == 35.0
    assert data.operating_margin == 22.0
    assert data.inventory_turnover == 4.0
    assert data.receivables_turnover == 6.0
    assert data.payables_turnover == 5.0
    assert data.asset_turnover == 0.5
    assert data.inventory_days == 91.25