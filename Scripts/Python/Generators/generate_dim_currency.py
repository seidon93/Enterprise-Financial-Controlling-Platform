"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : generate_dim_currency.py
Object Type     : Python Generator
Layer           : Data Generation
Version         : 1.0.0
Status          : Development

Description:
Generates and loads the EFAP Dim_Currency dimension into PostgreSQL.
===============================================================================
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

# Add Scripts/Python to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.config import settings
from common.database import engine


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


class DimCurrencyGenerator:

    def __init__(self):

        self.df = pd.DataFrame()

        self.source_file = (
            Path(__file__).resolve().parents[3]
            / "Data"
            / "Reference"
            / "currencies.csv"
        )

    def _load_source(self):

        logger.info("Loading currencies reference...")

        self.df = pd.read_csv(
            self.source_file,
            dtype=str,
        )

        logger.info("Loaded %s currencies.", len(self.df))

    def _transform(self):

        logger.info("Transforming currencies...")

        df = self.df.copy()

        # Surrogate Key
        df.insert(
            0,
            "currency_key",
            range(1, len(df) + 1),
        )

        # Boolean conversion
        df["is_reporting_currency"] = (
            df["is_reporting_currency"]
            .str.upper()
            .eq("TRUE")
        )

        df["is_active"] = True

        df["iso_numeric"] = df["iso_numeric"].astype(int)

        df["valid_from"] = "2020-01-01"
        df["valid_to"] = "9999-12-31"

        df = df[
            [
                "currency_key",
                "currency_code",
                "currency_name",
                "currency_symbol",
                "country",
                "iso_numeric",
                "is_reporting_currency",
                "is_active",
                "valid_from",
                "valid_to",
            ]
        ]

        self.df = df

        logger.info("Transformation finished.")

    def validate(self):

        logger.info("Validating Dim_Currency...")

        if self.df.empty:
            raise ValueError("DataFrame is empty.")

        if not self.df["currency_key"].is_unique:
            raise ValueError("CurrencyKey is not unique.")

        if not self.df["currency_code"].is_unique:
            raise ValueError("CurrencyCode is not unique.")

        logger.info("Validation successful.")

    def load(self):

        logger.info("Loading Dim_Currency into PostgreSQL...")

        with engine.begin() as connection:

            connection.execute(
                text(
                    f"TRUNCATE TABLE {settings.DB_SCHEMA}.dim_currency CASCADE;"
                )
            )

        self.df.to_sql(
            name="dim_currency",
            schema=settings.DB_SCHEMA,
            con=engine,  # type: ignore
            if_exists="append",
            index=False,
            method="multi",
        )

        logger.info("Loaded %d rows.", len(self.df))

    def generate(self):

        self._load_source()

        self._transform()

        return self.df

    def run(self):

        self.generate()

        self.validate()

        self.load()


if __name__ == "__main__":

    generator = DimCurrencyGenerator()

    generator.run()