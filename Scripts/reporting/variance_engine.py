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
    from Scripts.accounting.models import JournalEntry
except ModuleNotFoundError:
    from accounting.models import JournalEntry

try:
    from Scripts.budget.budget_line import BudgetLine
except ModuleNotFoundError:
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

    @staticmethod
    def compare_accounts(
        account_codes: list[str],
        budget_lines: list[BudgetLine],
        journal_entries: list[JournalEntry],
    ) -> list[VarianceResult]:

        results = []

        for account in account_codes:

            budget = VarianceEngine.budget_for_account(
                account,
                budget_lines,
            )

            actual = VarianceEngine.actual_for_account(
                account,
                journal_entries,
            )

            results.append(
                VarianceEngine.compare_account(
                    account_code=account,
                    budget=budget,
                    actual=actual,
                )
            )

        return results

    @staticmethod
    def total_variance(
        results: list[VarianceResult],
    ) -> Decimal:

        return sum(
            (r.variance for r in results),
            start=Decimal("0"),
        )

    @staticmethod
    def largest_variance(
        results: list[VarianceResult],
    ) -> VarianceResult:

        return max(
            results,
            key=lambda r: abs(r.variance),
        )