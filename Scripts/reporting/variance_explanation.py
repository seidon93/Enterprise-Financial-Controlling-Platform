"""
Enterprise Financial Analytics Platform (EFAP)

Variance Explanation Engine
"""

from decimal import Decimal


class VarianceExplanation:

    @staticmethod
    def explain(
        variance: Decimal,
        revenue_account: bool = False,
    ) -> str:

        if variance == 0:
            return "On Target"

        if revenue_account:

            if variance > 0:
                return "Favorable"

            return "Unfavorable"

        if variance < 0:
            return "Favorable"

        return "Unfavorable"