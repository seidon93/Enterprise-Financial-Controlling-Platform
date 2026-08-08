"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : price_volume_analysis_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 2.0.0
Status          : Development
Description     : Decomposes revenue change into price and volume effects.
===============================================================================
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PriceVolumeAnalysis:
    """
    Price versus volume revenue decomposition.
    """

    previous_price: float
    current_price: float

    previous_volume: float
    current_volume: float

    previous_revenue: float
    current_revenue: float

    price_effect: float
    volume_effect: float
    total_revenue_change: float


class PriceVolumeAnalysisService:
    """
    Decomposes revenue change into price and volume effects.

    The revenue bridge is anchored to the actual previous and current
    revenue values supplied by the controller layer.

    This guarantees:

        price_effect + volume_effect
        =
        current_revenue - previous_revenue
    """

    @staticmethod
    def calculate(
        previous_price: float,
        current_price: float,
        previous_volume: float,
        current_volume: float,
        previous_revenue: float | None = None,
        current_revenue: float | None = None,
    ) -> PriceVolumeAnalysis:

        # ------------------------------------------------------------------
        # Revenue baseline
        #
        # If explicit revenue values are supplied, they are treated as the
        # authoritative controller values.
        #
        # Otherwise revenue is derived from price × volume for backward
        # compatibility.
        # ------------------------------------------------------------------

        if previous_revenue is None:
            previous_revenue = (
                previous_price * previous_volume
            )

        if current_revenue is None:
            current_revenue = (
                current_price * current_volume
            )

        total_revenue_change = (
            current_revenue
            - previous_revenue
        )

        # ------------------------------------------------------------------
        # Price effect
        #
        # Price change is measured against the previous-period volume.
        # ------------------------------------------------------------------

        price_effect = (
            (current_price - previous_price)
            * previous_volume
        )

        # ------------------------------------------------------------------
        # Volume effect
        #
        # The remaining revenue movement is attributed to volume.
        #
        # This guarantees a mathematically complete bridge:
        #
        # Price Effect + Volume Effect = Total Revenue Change
        # ------------------------------------------------------------------

        volume_effect = (
            total_revenue_change
            - price_effect
        )

        return PriceVolumeAnalysis(
            previous_price=previous_price,
            current_price=current_price,
            previous_volume=previous_volume,
            current_volume=current_volume,
            previous_revenue=previous_revenue,
            current_revenue=current_revenue,
            price_effect=price_effect,
            volume_effect=volume_effect,
            total_revenue_change=total_revenue_change,
        )

