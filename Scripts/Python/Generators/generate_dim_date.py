"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : generate_dim_date.py
Object Type     : Python Generator
Layer           : Data Generation
Version         : 1.0.0
Status          : Development

Description:
Generates and loads the EFAP Dim_Date dimension into PostgreSQL.

Author:
EFAP Project

Dependencies:
    pandas
    pathlib
    logging
    datetime

===============================================================================
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import logging

# Add Scripts/Python to path so 'common' package is discoverable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from sqlalchemy import text

from common.database import engine


# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s")

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

@dataclass(slots=True)
class DimDateConfig:
    start_year: int = 2020
    end_year: int = 2035
    fiscal_year_start_month: int = 1
    culture: str = "en-US"

    @property
    def start_date(self) -> date:
        return date(self.start_year, 1, 1)

    @property
    def end_date(self) -> date:
        return date(self.end_year, 12, 31)


# =============================================================================
# Generator
# =============================================================================

class DimDateGenerator:

    def __init__(self, config: DimDateConfig):

        self.config = config
        self.df = pd.DataFrame()


    def generate(self) -> pd.DataFrame:

        logger.info("Generating calendar...")

        self.df = pd.DataFrame(
            {
                "full_date": pd.date_range(
                    self.config.start_date,
                    self.config.end_date,
                    freq="D",
                )
            }
        )

        self.df["date_key"] = (
            self.df["full_date"].dt.strftime("%Y%m%d").astype(int)
        )

        return self.df

# =============================================================================
# Validation
# =============================================================================

    def validate(self) -> None:

        logger.info("Validating Dim_Date...")

        if self.df.empty:
            raise ValueError("DataFrame is empty.")

        if not self.df["date_key"].is_unique:
            raise ValueError("DateKey is not unique.")

        if not self.df["full_date"].is_unique:
            raise ValueError("FullDate is not unique.")

        logger.info("Validation successful.")

# =============================================================================
# Load
# =============================================================================


    def load(self) -> None:

        logger.info("Loading Dim_Date into PostgreSQL...")

        with engine.begin() as connection:

            connection.execute(
                text("TRUNCATE TABLE warehouse.dim_date;")
            )

        self.df.to_sql(
            name="dim_date",
            schema="warehouse",
            con=engine,
            if_exists="append",
            index=False,
        )

        logger.info(
            "Loaded %s rows.",
            len(self.df),
        )

    def run(self) -> None:

        self.generate()

        self.validate()

        self.load()

if __name__ == "__main__":

    generator = DimDateGenerator(
        DimDateConfig()
    )

    generator.run()