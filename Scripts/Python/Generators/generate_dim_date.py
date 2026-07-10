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

        logger.info("Generating Dim_Date...")

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

        self._add_day_attributes()
        self._add_calendar_attributes()
        self._add_fiscal_attributes()
        self._add_period_attributes()
        self._add_business_flags()
        self._add_current_flags()

        logger.info("Generated %d rows.", len(self.df))

        return self.df

# =============================================================================
# Day Attributes
# =============================================================================

    def _add_day_attributes(self) -> None:

        logger.info("Adding day attributes...")

        self.df["day"] = self.df["full_date"].dt.day

        self.df["day_name"] = self.df["full_date"].dt.day_name()

        self.df["day_short_name"] = (
            self.df["day_name"]
            .str[:3]
        )

        # ISO: Monday = 1 ... Sunday = 7
        self.df["day_of_week"] = (
            self.df["full_date"]
            .dt.isocalendar()
            .day
            .astype(int)
        )

        self.df["week_of_year"] = (
            self.df["full_date"]
            .dt.isocalendar()
            .week
            .astype(int)
        )

        logger.info("Day attributes created.")

# =============================================================================
# Calendar Attributes
# =============================================================================

    def _add_calendar_attributes(self) -> None:

        logger.info("Adding calendar attributes...")

        dt = self.df["full_date"].dt

        self.df["calendar_month"] = dt.month
        self.df["month_name"] = dt.month_name()
        self.df["month_short_name"] = dt.strftime("%b")
        self.df["calendar_quarter"] = dt.quarter
        self.df["quarter_name"] = "Q" + dt.quarter.astype(str)
        self.df["calendar_year"] = dt.year

        logger.info("Calendar attributes created.")

# =============================================================================
# Fiscal Attributes
# =============================================================================

    def _add_fiscal_attributes(self) -> None:

        logger.info("Adding fiscal attributes...")

        dt = self.df["full_date"].dt
        fys = self.config.fiscal_year_start_month

        if fys == 1:
            self.df["fiscal_month"] = dt.month
            self.df["fiscal_quarter"] = dt.quarter
            self.df["fiscal_year"] = dt.year
        else:
            self.df["fiscal_month"] = (dt.month - fys) % 12 + 1
            self.df["fiscal_quarter"] = (self.df["fiscal_month"] - 1) // 3 + 1
            self.df["fiscal_year"] = dt.year + (dt.month >= fys).astype(int)

        logger.info("Fiscal attributes created.")

# =============================================================================
# Period Attributes
# =============================================================================

    def _add_period_attributes(self) -> None:

        logger.info("Adding period attributes...")

        dt = self.df["full_date"].dt

        self.df["year_month"] = dt.strftime("%Y-%m")
        self.df["year_month_key"] = dt.strftime("%Y%m").astype(int)

        self.df["month_start_date"] = (
            self.df["full_date"] - pd.to_timedelta(dt.day - 1, unit="D")
        )
        self.df["month_end_date"] = (
            self.df["month_start_date"] + pd.offsets.MonthEnd(0)
        )

        self.df["quarter_start_date"] = self.df["full_date"].apply(
            lambda d: pd.Timestamp(d.year, ((d.quarter - 1) * 3) + 1, 1)
        )
        self.df["quarter_end_date"] = (
            self.df["quarter_start_date"] + pd.offsets.QuarterEnd(0)
        )

        self.df["year_start_date"] = dt.year.apply(
            lambda y: pd.Timestamp(y, 1, 1)
        )
        self.df["year_end_date"] = dt.year.apply(
            lambda y: pd.Timestamp(y, 12, 31)
        )

        # Convert timestamps to date
        for col in [
            "full_date", "month_start_date", "month_end_date",
            "quarter_start_date", "quarter_end_date",
            "year_start_date", "year_end_date",
        ]:
            self.df[col] = pd.to_datetime(self.df[col]).dt.date

        logger.info("Period attributes created.")

# =============================================================================
# Business Flags
# =============================================================================

    def _add_business_flags(self) -> None:

        logger.info("Adding business flags...")

        dt = pd.to_datetime(self.df["full_date"]).dt

        self.df["is_weekend"] = (dt.dayofweek >= 5)
        self.df["is_working_day"] = ~self.df["is_weekend"]
        self.df["is_month_end"] = dt.is_month_end
        self.df["is_quarter_end"] = dt.is_quarter_end
        self.df["is_year_end"] = (dt.month == 12) & (dt.day == 31)

        logger.info("Business flags created.")

# =============================================================================
# Current Flags
# =============================================================================

    def _add_current_flags(self) -> None:

        logger.info("Adding current flags...")

        today = date.today()
        dt = pd.to_datetime(self.df["full_date"]).dt

        self.df["is_current_date"] = (self.df["full_date"] == today)
        self.df["is_current_month"] = (
            (dt.year == today.year) & (dt.month == today.month)
        )
        self.df["is_current_quarter"] = (
            (dt.year == today.year)
            & (dt.quarter == ((today.month - 1) // 3 + 1))
        )
        self.df["is_current_year"] = (dt.year == today.year)

        logger.info("Current flags created.")

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
