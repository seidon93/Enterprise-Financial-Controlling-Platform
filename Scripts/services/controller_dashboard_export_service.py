"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : controller_dashboard_export_service.py
Object Type     : Export Service
Layer           : Service Layer
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from dataclasses import asdict
from pathlib import Path

import pandas as pd

from services.controller_dashboard import (
    ControllerDashboard,
)


class ControllerDashboardExportService:
    """
    Exports controller dashboard data for downstream analytics tools.
    """

    @staticmethod
    def to_dataframe(
        dashboard: ControllerDashboard,
    ) -> pd.DataFrame:

        data = asdict(dashboard.data)

        return pd.DataFrame(
            [data]
        )

    @staticmethod
    def export_csv(
        dashboard: ControllerDashboard,
        output_path: str | Path,
    ) -> Path:

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        dataframe = (
            ControllerDashboardExportService
            .to_dataframe(dashboard)
        )

        dataframe.to_csv(
            output_path,
            index=False,
        )

        return output_path