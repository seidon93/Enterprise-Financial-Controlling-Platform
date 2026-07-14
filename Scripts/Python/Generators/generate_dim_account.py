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
# =============================================================================
# Transform
# =============================================================================

    def _transform(self) -> None:
        """
        Transform source data into Dim_Account.
        """

        logger.info("Transforming accounts...")
        # -------------------------------------------------------------------------
        # Account Key
        # -------------------------------------------------------------------------

        if "account_key" in self.df.columns:
            self.df.drop(columns=["account_key"], inplace=True)

        self.df.insert(
            0,
            "account_key",
            range(1, len(self.df) + 1),
        )

        # -------------------------------------------------------------------------
        # Account Class
        # -------------------------------------------------------------------------

        self.df["account_class"] = (
            self.df["account_number"]
            .str[0]
            .astype(int)
        )

        # -------------------------------------------------------------------------
        # Account Group
        # -------------------------------------------------------------------------

        self.df["account_group"] = (
            self.df["account_number"]
            .str[:2]
            .astype(int)
        )

        # -------------------------------------------------------------------------
        # Statement Type
        # -------------------------------------------------------------------------

        self.df["statement_type"] = (
            self.df["account_class"]
            .map(STATEMENT_TYPE)
        )

        # -------------------------------------------------------------------------
        # Reporting Group
        # -------------------------------------------------------------------------

        self.df["reporting_group"] = (
            self.df["account_class"]
            .map(REPORTING_GROUP)
        )

        # -------------------------------------------------------------------------
        # Reporting Category
        # -------------------------------------------------------------------------

        self.df["reporting_category"] = (
            self.df["account_class"]
            .map(REPORTING_CATEGORY)
        )

        # -------------------------------------------------------------------------
        # Normal Balance
        # -------------------------------------------------------------------------

        self.df["normal_balance"] = (
            self.df["account_class"]
            .map(NORMAL_BALANCE)
        )

        # -------------------------------------------------------------------------
        # Flags
        # -------------------------------------------------------------------------

        self.df["is_posting_account"] = True

        self.df["is_active"] = True

        # -------------------------------------------------------------------------
        # Validity
        # -------------------------------------------------------------------------

        self.df["valid_from"] = pd.to_datetime(self.config.valid_from)
        self.df["valid_to"] = pd.to_datetime(self.config.valid_to)

        # -------------------------------------------------------------------------
        # Final Column Order
        # -------------------------------------------------------------------------

        self.df = self.df[
            [
                "account_key",
                "account_number",
                "account_name",
                "account_type",
                "account_class",
                "account_group",
                "statement_type",
                "reporting_group",
                "reporting_category",
                "normal_balance",
                "is_posting_account",
                "is_active",
                "valid_from",
                "valid_to",
            ]
        ]

        logger.info("Transformation finished.")

    # =========================================================================
    # Generate
    # =========================================================================

    def generate(self) -> pd.DataFrame:

        logger.info("Generating Dim_Account...")

        self._load_source()

        self._transform()

        return self.df

    # =========================================================================
    # Validation
    # =========================================================================

    def validate(self) -> None:
        """
        Validate Dim_Account data.
        """

        logger.info("Validating Dim_Account...")

        if self.df.empty:
            raise ValueError("Dim_Account is empty.")

        if not self.df["account_key"].is_unique:
            raise ValueError("AccountKey contains duplicates.")

        if not self.df["account_number"].is_unique:
            raise ValueError("AccountNumber contains duplicates.")

        if self.df["account_name"].isnull().any():
            raise ValueError("AccountName contains NULL values.")

        if self.df["account_type"].isnull().any():
            raise ValueError("AccountType contains NULL values.")

        logger.info(
            "Validation successful (%d rows).",
            len(self.df),
        )

    # =========================================================================
    # Load
    # =========================================================================

    def load(self) -> None:
        """
        Load Dim_Account into PostgreSQL.
        """

        logger.info("Loading Dim_Account...")

        with engine.begin() as connection:

            connection.execute(
                text(
                    f"TRUNCATE TABLE {settings.DB_SCHEMA}.dim_account CASCADE;"
                )
            )

        self.df.to_sql(
            name="dim_account",
            schema=settings.DB_SCHEMA,
            con=engine,
            if_exists="append",
            index=False,
            method="multi",
        )

        logger.info(
            "Loaded %d rows into warehouse.dim_account.",
            len(self.df),
        )

    # =========================================================================
    # Run
    # =========================================================================

    def run(self) -> None:

        self.generate()

        self.validate()

        self.load()

        logger.info("Dim_Account completed successfully.")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    generator = DimAccountGenerator()

    generator.run()