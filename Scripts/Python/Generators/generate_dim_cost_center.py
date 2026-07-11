"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : generate_dim_cost_center.py
Object Type     : Python Generator
Layer           : Data Generation
Version         : 1.0.0
Status          : Development

Description:
Generates and loads the EFAP Dim_Cost_Center dimension into PostgreSQL.

Author:
EFAP Project

Dependencies:
    pandas
    sqlalchemy
    pathlib
    logging

===============================================================================
"""

from __future__ import annotations

from pathlib import Path
import sys
import logging

import pandas as pd
from sqlalchemy import text

# Add Scripts/Python to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.database import engine
from common.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)

# =============================================================================
# Generator
# =============================================================================

class DimCostCenterGenerator:

    def __init__(self):

        self.df = pd.DataFrame()

        self.source_file = (
            Path(__file__).resolve().parents[3]
            / "Data"
            / "Reference"
            / "cost_centers.csv"
        )


    def _load_source(self):

        logger.info("Loading cost centers reference...")

        self.df = pd.read_csv(
            self.source_file,
            dtype=str,
        )

        logger.info(
            "Loaded %s cost centers.",
            len(self.df),
        )



    def _transform(self):

        logger.info("Transforming cost centers...")

        df = self.df.copy()

        # ---------------------------------------------------------------------
        # Surrogate Key
        # ---------------------------------------------------------------------

        df.insert(
            0,
            "cost_center_key",
            range(1, len(df) + 1),
        )

        # ---------------------------------------------------------------------
        # Technical Columns
        # ---------------------------------------------------------------------

        df["is_active"] = True

        df["valid_from"] = "2020-01-01"

        df["valid_to"] = "9999-12-31"

        # ---------------------------------------------------------------------
        # Column Order
        # ---------------------------------------------------------------------

        df = df[
            [
                "cost_center_key",
                "cost_center_code",
                "cost_center_name",
                "parent_cost_center_code",
                "cost_center_level",
                "department_name",
                "manager_name",
                "location",
                "is_active",
                "valid_from",
                "valid_to",
            ]
        ]

        self.df = df

        logger.info("Transformation finished.")


    def validate(self):

        logger.info("Validating Dim_Cost_Center...")

        if self.df.empty:
            raise ValueError("DataFrame is empty.")

        if not self.df["cost_center_key"].is_unique:
            raise ValueError("CostCenterKey is not unique.")

        if not self.df["cost_center_code"].is_unique:
            raise ValueError("CostCenterCode is not unique.")

        logger.info("Validation successful.")


    def load(self):

        logger.info("Loading Dim_Cost_Center into PostgreSQL...")

        

    def generate(self):

        self._load_source()

        self._transform()

        return self.df


    def run(self):

        self.generate()

        self.validate()

        self.load()

# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    generator = DimCostCenterGenerator()

    generator.run()