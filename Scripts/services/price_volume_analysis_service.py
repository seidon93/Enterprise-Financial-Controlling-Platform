"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : price_volume_analysis_service.py
Object Type     : Service
Layer           : Service Layer
Version         : 1.0.0
Status          : Development
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
    """

    @staticmethod
    def calculate(
        previous_price: float,
        current_price: float,
        previous_volume: float,
        current_volume: float,
    ) -> PriceVolumeAnalysis:

        previous_price = previous_price
        current_price = current_price

        previous_volume = previous_volume
        current_volume = current_volume

        previous_revenue = (
            previous_price * previous_volume
        )

        current_revenue = (
            current_price * current_volume
        )

        price_effect = (
            (current_price - previous_price)
            * previous_volume
        )

        volume_effect = (
            (current_volume - previous_volume)
            * current_price
        )

        total_revenue_change = (
            current_revenue
            - previous_revenue
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