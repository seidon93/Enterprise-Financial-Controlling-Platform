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
Generates the EFAP Dim_Date dimension and exports it to CSV.

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

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import logging

import pandas as pd


# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
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


    def generate(self) -> pd.DataFrame:
        """
        Generate the complete Dim_Date dimension.
        """

        logger.info("Generating Dim_Date...")

        self._create_calendar()
        # self._add_day_attributes()
        # self._add_calendar_attributes()
        # self._add_fiscal_attributes()
        # self._add_period_attributes()
        # self._add_business_flags()
        # self._add_current_flags()
        # self._reorder_columns()
        # self._validate()

        logger.info("Dim_Date successfully generated.")

        return self.df

# =============================================================================
# Calendar
# =============================================================================

    def _create_calendar(self) -> None:
        """
        Create the base calendar DataFrame.
        """

        logger.info(
            "Creating calendar from %s to %s",
            self.config.start_date,
            self.config.end_date,
        )

        self.df = pd.DataFrame(
            {
                "FullDate": pd.date_range(
                    start=self.config.start_date,
                    end=self.config.end_date,
                    freq="D",
                )
            }
        )

        logger.info(
            "Calendar created (%d rows).",
            len(self.df),
        )
