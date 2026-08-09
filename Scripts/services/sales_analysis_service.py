"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : sales_analysis_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 1.0.0
Status          : Development
Description     : Calculates sales price and volume metrics from General Ledger.
===============================================================================
"""

from decimal import Decimal

from accounting.general_ledger_engine import GeneralLedgerEngine


class SalesAnalysisService:
    """Calculates controller sales metrics from posted GL entries."""

    SALES_REVENUE_ACCOUNT = "602"

    @staticmethod
    def calculate(
        general_ledger: GeneralLedgerEngine,
    ) -> dict[str, float]:

        total_volume = Decimal("0")
        total_revenue = Decimal("0")

        for entry in general_ledger.entries:
            for line in entry.lines:

                if line.account_number != SalesAnalysisService.SALES_REVENUE_ACCOUNT:
                    continue

                if line.quantity is None:
                    continue

                if line.unit_price is None:
                    continue

                quantity = line.quantity
                unit_price = line.unit_price

                total_volume += quantity
                total_revenue += quantity * unit_price

        if total_volume == Decimal("0"):
            return {
                "volume": 0.0,
                "average_price": 0.0,
                "revenue": 0.0,
            }

        average_price = (
            total_revenue / total_volume
        )

        return {
            "volume": float(total_volume),
            "average_price": float(average_price),
            "revenue": float(total_revenue),
        }
