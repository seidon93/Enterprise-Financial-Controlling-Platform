from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class VarianceResult:

    budget: Decimal
    actual: Decimal
    variance: Decimal
    variance_percent: Decimal

from decimal import Decimal


class VarianceEngine:

    @staticmethod
    def calculate(
        budget: Decimal,
        actual: Decimal,
    ) -> VarianceResult:

        variance = actual - budget

        if budget == 0:
            percent = Decimal("0")
        else:
            percent = (variance / budget) * Decimal("100")

        return VarianceResult(
            budget=budget,
            actual=actual,
            variance=variance,
            variance_percent=percent,
        )