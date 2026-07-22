"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : asset_event_generator.py
Object Type     : Asset Business Event Generator
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates asset business events from asset transactions.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domain.asset_event import AssetEvent
from domain.asset_provider import AssetProvider
from domain.business_event_type import BusinessEventType


class AssetEventGenerator:
    """
    Generates business events related to enterprise assets.
    """

    def __init__(
        self,
        provider: AssetProvider,
    ) -> None:

        self.provider = provider

    def asset_acquisition_event(
        self,
    ) -> AssetEvent:
        """
        Generate one asset acquisition business event.
        """

        asset = self.provider.random_asset()

        return AssetEvent(

            event_type=BusinessEventType.ASSET_ACQUISITION,

            company_code=asset.company_code,

            asset_code=asset.asset_code,
            asset_name=asset.asset_name,
            asset_category=asset.asset_category,

            supplier_code=asset.supplier_code,

            event_date=asset.acquisition_date,

            acquisition_cost=asset.acquisition_cost,

            vat_rate=asset.vat_rate,

            useful_life_months=asset.useful_life_months,

            depreciation_method=asset.depreciation_method,

            salvage_value=asset.salvage_value,

            currency_code=asset.currency_code,

            cost_center_code=asset.cost_center_code,

            department_code=asset.department_code,
        )