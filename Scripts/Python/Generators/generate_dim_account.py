"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : generate_dim_account.py
Object Type     : Python Generator
Layer           : Data Generation
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------

Description:
Generates the General Ledger Account Dimension (Dim_Account)
and loads it into PostgreSQL.

Author:
EFAP Project

Dependencies:
    pandas
    sqlalchemy
    pathlib
    logging
    datetime

===============================================================================
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd
from sqlalchemy import text

import sys

# Add Scripts/Python to path so 'common' package is discoverable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.database import engine
from common.config import settings
from common.mappings import (
    STATEMENT_TYPE,
    NORMAL_BALANCE,
    REPORTING_GROUP,
    REPORTING_CATEGORY,
)


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
class DimAccountConfig:

    reference_file: str = "accounts.csv"

    valid_from: date = date(2020, 1, 1)

    valid_to: date = date(9999, 12, 31)


# =============================================================================
# Generator
# =============================================================================

class DimAccountGenerator:

    def __init__(self, config: DimAccountConfig | None = None):

        self.config = config or DimAccountConfig()

        self.project_root = Path(__file__).resolve().parents[3]

        self.reference_path = (
            self.project_root
            / "Data"
            / "Reference"
        )

        self.df = pd.DataFrame()

    # =========================================================================
    # Source
    # =========================================================================

    def _load_source(self) -> None:
        """
        Load Chart of Accounts reference file.
        """

        logger.info("Loading accounts reference...")

        source_file = (
            self.reference_path
            / self.config.reference_file
        )

        self.df = pd.read_csv(
            source_file,
            dtype={
                "account_number": str
            },
            encoding="utf-8",
        )

        logger.info(
            "Loaded %d accounts.",
            len(self.df),
        )

    # =========================================================================
    # Generate
    # =========================================================================

    def generate(self) -> pd.DataFrame:

        logger.info("Generating Dim_Account...")

        self._load_source()

        return self.df

if __name__ == "__main__":

    generator = DimAccountGenerator()

    df = generator.generate()

    print(df.head())

    print(df.dtypes)