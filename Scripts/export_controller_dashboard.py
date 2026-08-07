"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : export_controller_dashboard.py
Object Type     : Export Runner
Layer           : Application Layer
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from pathlib import Path

from reporting.balance_sheet import BalanceSheet
from reporting.income_statement import IncomeStatement
from reporting.trial_balance import TrialBalance

from services.controller_dashboard_service import (
    ControllerDashboardService,
)
from services.controller_dashboard_export_service import (
    ControllerDashboardExportService,
)
from services.financial_controller_report import (
    FinancialControllerReport,
)


def build_report() -> FinancialControllerReport:

    tb = TrialBalance()

    return FinancialControllerReport(
        trial_balance=tb,
        income_statement=IncomeStatement(tb),
        balance_sheet=BalanceSheet(tb),
        financial_ratios={
            "current_ratio": 0.0,
            "quick_ratio": 0.0,
            "cash_ratio": 0.0,
            "net_margin": 0.0,
            "gross_margin": 0.0,
            "operating_margin": 0.0,
            "return_on_assets": 0.0,
            "return_on_equity": 0.0,
            "inventory_turnover": 0.0,
            "receivables_turnover": 0.0,
            "payables_turnover": 0.0,
            "asset_turnover": 0.0,
            "inventory_days": 0.0,
            "working_capital": 0.0,
            "working_capital_ratio": 0.0,
        },
    )


def main() -> None:

    project_root = Path(__file__).resolve().parents[1]

    output_path = (
        project_root
        / "data"
        / "processed"
        / "controller_dashboard.csv"
    )

    report = build_report()

    dashboard = ControllerDashboardService.create(
        report
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