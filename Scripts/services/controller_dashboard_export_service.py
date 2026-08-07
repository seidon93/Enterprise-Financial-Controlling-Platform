"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : controller_dashboard_export_service.py
Object Type     : Export Service
Layer           : Service Layer
Version         : 1.1.0
Status          : Development
===============================================================================
"""

from pathlib import Path

import pandas as pd

from services.controller_dashboard import (
    ControllerDashboard,
)


class ControllerDashboardExportService:
    """
    Exports controller dashboard data for downstream analytics tools.
    """

    EXPORT_COLUMNS = (
        "revenue",
        "expenses",
        "net_profit",
        "current_ratio",
        "quick_ratio",
        "cash_ratio",
        "net_margin",
        "gross_margin",
        "operating_margin",
        "return_on_assets",
        "return_on_equity",
        "inventory_turnover",
        "receivables_turnover",
        "payables_turnover",
        "asset_turnover",
        "inventory_days",
        "working_capital",
        "working_capital_ratio",
        "revenue_budget",
        "revenue_variance",
        "revenue_variance_pct",
        "revenue_variance_status",
        "expense_budget",
        "expense_variance",
        "expense_variance_pct",
        "expense_variance_status",
        "budget_net_profit",
        "net_profit_variance",
        "net_profit_variance_pct",
        "net_profit_variance_status",
        "revenue_previous_year",
        "revenue_yoy_change",
        "revenue_yoy_change_pct",
        "revenue_yoy_status",
        "net_profit_previous_year",
        "net_profit_yoy_change",
        "net_profit_yoy_change_pct",
        "net_profit_yoy_status",
        "previous_price",
        "current_price",
        "previous_volume",
        "current_volume",
        "price_effect",
        "volume_effect",
        "total_revenue_change",
        "standard_cost",
        "actual_cost",
        "cost_variance",
        "cost_variance_pct",
        "cost_variance_status",
    )

    @classmethod
    def to_dataframe(
        cls,
        dashboard: ControllerDashboard,
    ) -> pd.DataFrame:

        data = dashboard.data

        row = {
            column: getattr(data, column)
            for column in cls.EXPORT_COLUMNS
        }

        return pd.DataFrame([row])

    @classmethod
    def export_csv(
        cls,
        dashboard: ControllerDashboard,
        output_path: str | Path,
    ) -> Path:

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        dataframe = cls.to_dataframe(
            dashboard
        )

        dataframe.to_csv(
            output_path,
            index=False,
        )

        return output_path