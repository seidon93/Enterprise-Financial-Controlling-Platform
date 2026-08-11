"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : load_dim_asset.py
Object Type     : Dimension Loader
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates and loads enterprise fixed assets into warehouse.dim_asset.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
import pandas as pd

from common.config import settings
from common.database import engine
from scenarios.assets.asset_provider import AssetProvider
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

TOTAL_ASSETS = 5_000


def load_dim_asset() -> None:

    provider = AssetProvider(seed=42)

    assets = []

    for asset_id in range(1, TOTAL_ASSETS + 1):

        asset = provider.create_asset(asset_id)

        assets.append({
            "asset_code": asset.asset_code,
            "asset_name": asset.asset_name,
            "asset_class": asset.asset_class,
            "asset_group": asset.asset_group,
            "company_code": asset.company_code,
            "supplier_code": asset.supplier_code,
            "currency_code": asset.currency_code,
            "acquisition_date": asset.acquisition_date,
            "capitalization_date": asset.capitalization_date,
            "depreciation_start_date": asset.depreciation_start_date,
            "acquisition_cost": float(asset.acquisition_cost),
            "residual_value": float(asset.residual_value),
            "useful_life_months": asset.useful_life_months,
            "depreciation_method": asset.depreciation_method,
            "cost_center_code": asset.cost_center_code,
            "department_code": asset.department_code,
            "country_code": asset.country_code,
            "city": asset.city,
            "location": asset.location,
            "vat_rate": float(asset.vat_rate),
            "is_active": asset.is_active,
            "disposal_date": asset.disposal_date,
            "is_current": True,
        })

    df = pd.DataFrame(assets)

    # Deduplicate on asset_code (random_asset can produce duplicates)
    df = df.drop_duplicates(subset=["asset_code"], keep="first")

    with engine.begin() as connection:

        connection.execute(
            text(
                f"TRUNCATE TABLE {settings.DB_SCHEMA}.dim_asset CASCADE;"
            )
        )

    df.to_sql(
        name="dim_asset",
        schema=settings.DB_SCHEMA,
        con=engine,  # type: ignore
        if_exists="append",
        index=False,
    )

    logger.info(
        "Loaded %s assets into dim_asset.",
        len(df),
    )


if __name__ == "__main__":
    load_dim_asset()
