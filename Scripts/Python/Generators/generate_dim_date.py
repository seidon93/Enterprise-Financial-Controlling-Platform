# pyright: reportAttributeAccessIssue=false
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

from common.calendar import (  # type: ignore
    CZECH_DAY_NAMES,
    CZECH_DAY_SHORT_NAMES,
    CZECH_MONTH_NAMES,
    CZECH_MONTH_SHORT_NAMES,
    QUARTER_NAMES,
    get_today,
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
# Generator
# =============================================================================

class DimDateGenerator:

    def __init__(self):

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

    # =========================================================================
    # Day Attributes
    # =========================================================================

    def _add_day_attributes(self) -> None:
        """
        Add day related attributes.
        """

        logger.info("Adding day attributes...")

        iso = self.df["full_date"].dt.isocalendar()  # type: ignore

        self.df["date_key"] = self.df["full_date"].dt.strftime("%Y%m%d").astype(int)  # type: ignore
        self.df["day"] = self.df["full_date"].dt.day.astype(int)  # type: ignore
        self.df["day_of_week"] = iso.day.astype(int)  # type: ignore
        self.df["week_of_year"] = iso.week.astype(int)  # type: ignore
        self.df["day_name"] = self.df["day_of_week"].map(CZECH_DAY_NAMES)
        self.df["day_short_name"] = self.df["day_of_week"].map(CZECH_DAY_SHORT_NAMES)

        logger.info("Day attributes created.")

    # =========================================================================
    # Calendar Attributes
    # =========================================================================

    def _add_calendar_attributes(self) -> None:
        """
        Add calendar attributes.
        """

        logger.info("Adding calendar attributes...")

        self.df["calendar_month"] = self.df["full_date"].dt.month.astype(int)  # type: ignore
        self.df["month_name"] = self.df["calendar_month"].map(CZECH_MONTH_NAMES)
        self.df["month_short_name"] = self.df["calendar_month"].map(CZECH_MONTH_SHORT_NAMES)
        self.df["calendar_quarter"] = self.df["full_date"].dt.quarter.astype(int)  # type: ignore
        self.df["quarter_name"] = self.df["calendar_quarter"].map(QUARTER_NAMES)
        self.df["calendar_year"] = self.df["full_date"].dt.year.astype(int)  # type: ignore

        logger.info("Calendar attributes created.")

# ============================================================================
# Fiscal Attributes
# ============================================================================

    def _add_fiscal_attributes(self) -> None:
        """
        Add fiscal calendar attributes.
        """

        logger.info("Adding fiscal attributes...")

        fiscal_start = settings.FISCAL_YEAR_START_MONTH

        self.df["fiscal_month"] = (
            ((self.df["calendar_month"] - fiscal_start) % 12 + 1)
            .astype(int)
        )

        self.df["fiscal_quarter"] = (
            ((self.df["fiscal_month"] - 1) // 3 + 1)
            .astype(int)
        )

        self.df["fiscal_year"] = (
            self.df["calendar_year"]
            + (self.df["calendar_month"] >= fiscal_start).astype(int)
            - 1
        ).astype(int)

        logger.info("Fiscal attributes created.")

# =============================================================================
# Period Attributes
# =============================================================================


    def _add_period_attributes(self) -> None:
        """
        Add period related attributes.
        """

        logger.info("Adding period attributes...")

        self.df["year_month"] = (
            self.df["calendar_year"].astype(str)
            + "-"
            + self.df["calendar_month"].astype(str).str.zfill(2)
        )

        self.df["year_month_key"] = (
            self.df["calendar_year"] * 100
            + self.df["calendar_month"]
        )

        self.df["month_start_date"] = self.df["full_date"].dt.to_period("M").dt.start_time  # type: ignore
        self.df["month_end_date"] = self.df["full_date"].dt.to_period("M").dt.end_time.dt.normalize()  # type: ignore
        self.df["quarter_start_date"] = self.df["full_date"].dt.to_period("Q").dt.start_time  # type: ignore
        self.df["quarter_end_date"] = self.df["full_date"].dt.to_period("Q").dt.end_time.dt.normalize()  # type: ignore

        self.df["year_start_date"] = (
            pd.to_datetime(
                self.df["calendar_year"].astype(str) + "-01-01"
            )
        )

        self.df["year_end_date"] = (
            pd.to_datetime(
                self.df["calendar_year"].astype(str) + "-12-31"
            )
        )

        logger.info("Period attributes created.")

# =============================================================================
# Business Flags
# =============================================================================


    def _add_business_flags(self) -> None:
        """
        Add business flags.
        """

        logger.info("Adding business flags...")

        self.df["is_weekend"] = (
            self.df["day_of_week"] >= 6
        )

        self.df["is_working_day"] = (
            ~self.df["is_weekend"]
        )

        self.df["is_month_end"] = (
            self.df["full_date"]
            == self.df["month_end_date"]
        )

        self.df["is_quarter_end"] = (
            self.df["full_date"]
            == self.df["quarter_end_date"]
        )

        self.df["is_year_end"] = (
            self.df["full_date"]
            == self.df["year_end_date"]
        )

        logger.info("Business flags created.")

# =============================================================================
# Current Flags
# =============================================================================

    def _add_current_flags(self) -> None:
        """
        Add current period flags.
        """

        logger.info("Adding current flags...")

        today = pd.Timestamp(get_today())

        current_year = today.year
        current_month = today.month
        current_quarter = ((today.month - 1) // 3) + 1

        self.df["is_current_date"] = (
            self.df["full_date"] == today
        )

        self.df["is_current_month"] = (
            (self.df["calendar_year"] == current_year)
            &
            (self.df["calendar_month"] == current_month)
        )

        self.df["is_current_quarter"] = (
            (self.df["calendar_year"] == current_year)
            &
            (self.df["calendar_quarter"] == current_quarter)
        )

        self.df["is_current_year"] = (
            self.df["calendar_year"] == current_year
        )

        logger.info("Current flags created.")

# =========================================================================
# Final Column Order
# =========================================================================

    def _reorder_columns(self) -> None:
        """
        Reorder columns according to the enterprise data model.
        """

        logger.info("Reordering columns...")

        self.df = self.df[
            [
                "date_key",
                "full_date",
                "day",
                "day_name",
                "day_short_name",
                "day_of_week",
                "week_of_year",
                "calendar_month",
                "month_name",
                "month_short_name",
                "calendar_quarter",
                "quarter_name",
                "calendar_year",
                "fiscal_month",
                "fiscal_quarter",
                "fiscal_year",
                "year_month",
                "year_month_key",
                "month_start_date",
                "month_end_date",
                "quarter_start_date",
                "quarter_end_date",
                "year_start_date",
                "year_end_date",
                "is_weekend",
                "is_working_day",
                "is_month_end",
                "is_quarter_end",
                "is_year_end",
                "is_current_date",
                "is_current_month",
                "is_current_quarter",
                "is_current_year",
            ]
        ]

        logger.info("Columns reordered.")

# =============================================================================
# Validation
# =============================================================================

    def validate(self) -> None:

        logger.info("Validating Dim_Date...")

        self._validate_dataframe()

        logger.info("Validation successful.")

    def _validate_dataframe(self) -> None:
        """
        Validate generated dataframe.
        """

        if self.df.empty:
            raise ValueError("Dim_Date dataframe is empty.")

        if not self.df["date_key"].is_unique:
            raise ValueError("date_key must be unique.")

        if not self.df["full_date"].is_unique:
            raise ValueError("full_date must be unique.")

        if self.df.isnull().any().any():
            raise ValueError("Dim_Date contains NULL values.")

# =============================================================================
# Load
# =============================================================================

    def load(self) -> None:

        logger.info("Loading Dim_Date into PostgreSQL...")

        with engine.begin() as connection:

            connection.execute(
                text(
                    f"TRUNCATE TABLE {settings.DB_SCHEMA}.dim_date CASCADE;"
                )
            )

        self.df.to_sql(
            name="dim_date",
            schema=settings.DB_SCHEMA,
            con=engine,  # type: ignore
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

# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    generator = DimDateGenerator()

    generator.run()


