from dataclasses import dataclass
from decimal import Decimal
from Scripts.reporting.variace_engine import VarianceEngine


@dataclass(slots=True)
class VarianceAnalysisRow:

    key: str

    budget: Decimal

    actual: Decimal

    variance: Decimal

    variance_percent: Decimal

class VarianceAnalysis:

    @staticmethod
    def by_account(
        budget: dict[str, Decimal],
        actual: dict[str, Decimal],
    ) -> list[VarianceAnalysisRow]:

        rows = []

        accounts = sorted(set(budget) | set(actual))

        for account in accounts:

            b = budget.get(account, Decimal("0"))
            a = actual.get(account, Decimal("0"))

            result = VarianceEngine.calculate(b, a)

            rows.append(

                VarianceAnalysisRow(
                    key=account,
                    budget=b,
                    actual=a,
                    variance=result.variance,
                    variance_percent=result.variance_percent,
                )

            )

        return rows