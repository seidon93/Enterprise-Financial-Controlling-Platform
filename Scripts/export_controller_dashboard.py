"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : export_controller_dashboard.py
Object Type     : Controller Dashboard Export Runner
Layer           : Application / Reporting
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from pathlib import Path

from services.controller_dashboard_export_service import (
    ControllerDashboardExportService,
)

from services.controller_dashboard_service import (
    ControllerDashboardService,
)

from workflows.financial_controller_workflow import (
    run_financial_controller_workflow,
)


def main() -> None:
    """
    Execute the complete Financial Controller workflow
    and export the resulting dashboard to CSV.
    """

    project_root = Path(__file__).resolve().parents[1]

    output_path = (
        project_root
        / "data"
        / "processed"
        / "controller_dashboard.csv"
    )

    # -------------------------------------------------------------------------
    # Execute production Financial Controller workflow
    #
    # Scenario
    #     ↓
    # JournalRepository
    #     ↓
    # GeneralLedgerEngine
    #     ↓
    # FinancialControllerService
    # -------------------------------------------------------------------------

    report = run_financial_controller_workflow()

    # -------------------------------------------------------------------------
    # Build Controller Dashboard
    # -------------------------------------------------------------------------

    dashboard = ControllerDashboardService.create(
        report
    )

    # -------------------------------------------------------------------------
    # Export dashboard
    # -------------------------------------------------------------------------

    ControllerDashboardExportService.export_csv(
        dashboard=dashboard,
        output_path=output_path,
    )

    print(
        "Controller dashboard exported to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()