"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : generate_dim_date.py
Object Type     : ETL Generator
Layer           : Data Generation
Version         : 2.0.0
Status          : Production
-------------------------------------------------------------------------------

Description:
Generates the enterprise Dim_Date dimension and loads it into PostgreSQL.

===============================================================================
"""

from __future__ import annotations
from dataclasses import dataclass

import sys
from pathlib import Path

# Add Scripts/Python to the path so 'common' package can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
from datetime import date

import pandas as pd
from sqlalchemy import text

from common.calendar import (
    CZECH_DAY_NAMES,
    CZECH_DAY_SHORT_NAMES,
    CZECH_MONTH_NAMES,
    CZECH_MONTH_SHORT_NAMES,
    QUARTER_NAMES,
)

from common.config import settings
from common.database import engine


# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

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

    # =========================================================================
    # Public API
    # =========================================================================

    def run(self) -> None:

        logger.info("Starting Dim_Date generation...")

        self.generate()

        self.validate()

        self.load()

        logger.info("Dim_Date finished successfully.")


    def generate(self) -> pd.DataFrame:

        logger.info("Generating Dim_Date...")

        self._create_calendar()

        self._add_day_attributes()

        self._add_calendar_attributes()

        self._add_fiscal_attributes()

        self._add_period_attributes()

        self._add_business_flags()

        self._add_current_flags()

        self._reorder_columns()

        return self.df

# =============================================================================
# Calendar Creation
# =============================================================================

    def _create_calendar(self) -> None:

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

    # =========================================================================
    # Day Attributes
    # =========================================================================

    def _add_day_attributes(self) -> None:
        """
        Add day related attributes.
        """

        logger.info("Adding day attributes...")

        iso = self.df["full_date"].dt.isocalendar()

        self.df["date_key"] = (
            self.df["full_date"]
            .dt.strftime("%Y%m%d")
            .astype(int)
        )

        self.df["day"] = (
            self.df["full_date"]
            .dt.day
            .astype(int)
        )

        self.df["day_of_week"] = (
            iso.day.astype(int)
        )

        self.df["week_of_year"] = (
            iso.week.astype(int)
        )

        self.df["day_name"] = (
            self.df["day_of_week"]
            .map(CZECH_DAY_NAMES)
        )

        self.df["day_short_name"] = (
            self.df["day_of_week"]
            .map(CZECH_DAY_SHORT_NAMES)
        )

        logger.info("Day attributes created.")

    # =========================================================================
    # Calendar Attributes
    # =========================================================================

    def _add_calendar_attributes(self) -> None:
        """
        Add calendar attributes.
        """

        logger.info("Adding calendar attributes...")

        self.df["calendar_month"] = (
            self.df["full_date"]
            .dt.month
            .astype(int)
        )

        self.df["month_name"] = (
            self.df["calendar_month"]
            .map(CZECH_MONTH_NAMES)
        )

        self.df["month_short_name"] = (
            self.df["calendar_month"]
            .map(CZECH_MONTH_SHORT_NAMES)
        )

        self.df["calendar_quarter"] = (
            self.df["full_date"]
            .dt.quarter
            .astype(int)
        )

        self.df["quarter_name"] = (
            self.df["calendar_quarter"]
            .map(QUARTER_NAMES)
        )

        self.df["calendar_year"] = (
            self.df["full_date"]
            .dt.year
            .astype(int)
        )

        logger.info("Calendar attributes created.")

# ============================================================================
# Fiscal Attributes
# ============================================================================

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
# Reorder Columns
# =============================================================================

    def _reorder_columns(self) -> None:

        # Move date_key to the front
        cols = ["date_key"] + [
            c for c in self.df.columns if c != "date_key"
        ]
        self.df = self.df[cols]

        logger.info("Generated %d rows.", len(self.df))

# =============================================================================
# Validation
# =============================================================================

    def validate(self) -> None:

        logger.info("Validating Dim_Date...")

        self._validate_dataframe()

        logger.info("Validation successful.")

    def _validate_dataframe(self) -> None:

        if self.df.empty:
            raise ValueError("DataFrame is empty.")

        if not self.df["date_key"].is_unique:
            raise ValueError("DateKey is not unique.")

        if not self.df["full_date"].is_unique:
            raise ValueError("FullDate is not unique.")

# =============================================================================
# Load
# =============================================================================

    def load(self) -> None:

        logger.info("Loading Dim_Date into PostgreSQL...")

        with engine.begin() as connection:

            connection.execute(
                text(
                    f"TRUNCATE TABLE {settings.DB_SCHEMA}.dim_date;"
                )
            )

        self.df.to_sql(
            name="dim_date",
            schema=settings.DB_SCHEMA,
            con=engine,
            if_exists="append",
            index=False,
        )

        logger.info(
            "Loaded %s rows.",
            len(self.df),
        )

    # =========================================================================
    # Calendar
    # =========================================================================

    def _create_calendar(self) -> None:
        """
        Create the base calendar DataFrame.
        """

        logger.info("Creating calendar...")

        start_date = date(settings.CALENDAR_START_YEAR, 1, 1)
        end_date = date(settings.CALENDAR_END_YEAR, 12, 31)

        self.df = pd.DataFrame(
            {
                "full_date": pd.date_range(
                    start=start_date,
                    end=end_date,
                    freq="D",
                )
            }
        )

        logger.info(
            "Calendar created (%s rows).",
            len(self.df),
        )

if __name__ == "__main__":

    generator = DimDateGenerator(
        DimDateConfig()
    )

    generator.run()
