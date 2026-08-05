"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : variance_engine.py
Object Type     : Reporting Engine
Layer           : Reporting
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from decimal import Decimal

try:
    from .variance_result import VarianceResult
except ImportError:
    from variance_result import VarianceResult


try:
    from accounting.models import JournalEntry
except ModuleNotFoundError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from accounting.models import JournalEntry

try:
    from budget.budget_line import BudgetLine
except ModuleNotFoundError:
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from budget.budget_line import BudgetLine




class VarianceEngine:

    @staticmethod
    def compare(
        budget: Decimal,
        actual: Decimal,
    ) -> VarianceResult:

        variance = actual - budget

        if budget == Decimal("0"):
            variance_percent = Decimal("0")
        else:
            variance_percent = (
                variance / budget
            ) * Decimal("100")

        return VarianceResult(
            account_code="",
            budget=budget,
            actual=actual,
            variance=variance,
            variance_percent=variance_percent,
            favorable=variance >= Decimal("0"),
        )

    @staticmethod
    def compare_account(
        *,
        account_code: str,
        budget: Decimal,
        actual: Decimal,
    ) -> VarianceResult:

        variance = actual - budget

        if budget == Decimal("0"):
            percent = Decimal("0")
        else:
            percent = variance / budget * Decimal("100")

        return VarianceResult(
            account_code=account_code,
            budget=budget,
            actual=actual,
            variance=variance,
            variance_percent=percent,
            favorable=variance <= Decimal("0") if account_code.startswith("5") else variance >= Decimal("0"),
        )


    @staticmethod
    def actual_for_account(
        account_code: str,
        journal_entries: list[JournalEntry],
    ) -> Decimal:

        total = Decimal("0")

        for entry in journal_entries:

            for line in entry.lines:

                if line.account_number == account_code:

                    total += line.debit_amount

                    total -= line.credit_amount

        return total

    @staticmethod
    def budget_for_account(
        account_code: str,
        budget_lines: list,
    ) -> Decimal:

        total = Decimal("0")

        for line in budget_lines:

            if line.account_number == account_code:

                total += line.amount

        return total