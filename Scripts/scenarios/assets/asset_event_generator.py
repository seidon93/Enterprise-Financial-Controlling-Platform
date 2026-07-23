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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


from domain.business_event_type import BusinessEventType

from scenarios.assets.asset_event import AssetEvent
from scenarios.assets.asset_provider import AssetProvider
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
            asset_class=asset.asset_class,
            asset_group=asset.asset_group,

            supplier_code=asset.supplier_code,

            event_date=asset.acquisition_date,

            acquisition_cost=asset.acquisition_cost,

            vat_rate=asset.vat_rate,

            useful_life_months=asset.useful_life_months,

            depreciation_method=asset.depreciation_method,

            residual_value=asset.residual_value,

            country_code=asset.country_code,

            city=asset.city,

            location=asset.location,

            capitalization_date=asset.capitalization_date,

            depreciation_start_date=asset.depreciation_start_date,
        )