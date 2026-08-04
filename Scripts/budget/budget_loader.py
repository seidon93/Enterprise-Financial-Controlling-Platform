"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : budget_loader.py
Object Type     : Budget Loader
Layer           : Budget
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Loads budgets from external sources.
===============================================================================
"""

from __future__ import annotations
import csv
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from decimal import Decimal

from Scripts.budget.budget_line import BudgetLine

class BudgetLoader:

    def load_csv(
        self,
        path: Path,
    ):

        if not path.exists():
            raise FileNotFoundError(path)

        with path.open(
            newline="",
            encoding="utf-8",
        ) as file:

            reader = csv.DictReader(file)

            return list(reader)

    def to_budget_line(
        self,
        row: dict,
    ) -> BudgetLine:

        return BudgetLine(
            company_code=row["company"],
            account_number=row["account"],
            cost_center_code=row["cost_center"],
            department_code=row["department"],
            fiscal_year=int(row["fiscal_year"]),
            fiscal_period=int(row["fiscal_period"]),
            amount=Decimal(row["amount"]),
        )

    
    def load_budget_lines(
        self,
        path: Path,
    ):

        rows = self.load_csv(path)

        return [
            self.to_budget_line(row)
            for row in rows
        ]