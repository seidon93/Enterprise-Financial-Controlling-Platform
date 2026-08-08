"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : export_controller_dashboard.py
Object Type     : Export Runner
Layer           : Application Layer
Version         : 2.0.0
Status          : Development
===============================================================================
"""

from pathlib import Path

from accounting.general_ledger_engine import GeneralLedgerEngine
from repositories.journal_repository import JournalRepository

from services.controller_dashboard_export_service import (
    ControllerDashboardExportService,
)
from services.controller_dashboard_service import (
    ControllerDashboardService,
)
from services.financial_controller_service import (
    FinancialControllerService,
)


def build_general_ledger(
    journal_repository: JournalRepository,
) -> GeneralLedgerEngine:

    ledger = GeneralLedgerEngine()

    for entry in journal_repository.get_all():
        ledger.post(entry)

    return ledger


def create_dashboard(
    journal_repository: JournalRepository,
):

    general_ledger = build_general_ledger(
        journal_repository
    )

    report = FinancialControllerService.create_report(
        general_ledger
    )

    return ControllerDashboardService.create(
        report
    )


def main() -> None:

    project_root = Path(__file__).resolve().parents[1]

    output_path = (
        project_root
        / "data"
        / "processed"
        / "controller_dashboard.csv"
    )

    journal_repository = JournalRepository()

    dashboard = create_dashboard(
        journal_repository
    )

    ControllerDashboardExportService.export_csv(
        dashboard=dashboard,
        output_path=output_path,
    )

    print(
        f"Controller dashboard exported to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()