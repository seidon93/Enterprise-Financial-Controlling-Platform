"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : generate_dim_department.py
Object Type     : Python Generator
Layer           : Data Generation
Version         : 1.0.0
Status          : Development

Description:
Generates and loads the EFAP Dim_Department dimension into PostgreSQL.
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


class DimDepartmentGenerator:

    def __init__(self):

        self.df = pd.DataFrame()

        self.source_file = (
            Path(__file__).resolve().parents[3]
            / "Data"
            / "Reference"
            / "departments.csv"
        )

    def _load_source(self):

        logger.info("Loading departments reference...")

        self.df = pd.read_csv(
            self.source_file,
            dtype=str,
        )

        logger.info("Loaded %s departments.", len(self.df))

    def _transform(self):

        logger.info("Transforming departments...")

        df = self.df.copy()

        df.insert(
            0,
            "department_key",
            range(1, len(df) + 1),
        )

        df["is_active"] = True
        df["valid_from"] = "2020-01-01"
        df["valid_to"] = "9999-12-31"

        df = df[
            [
                "department_key",
                "department_code",
                "department_name",
                "division_name",
                "director_name",
                "location",
                "is_active",
                "valid_from",
                "valid_to",
            ]
        ]

        self.df = df

        logger.info("Transformation finished.")

    def validate(self):

        logger.info("Validating Dim_Department...")

        if self.df.empty:
            raise ValueError("DataFrame is empty.")

        if not self.df["department_key"].is_unique:
            raise ValueError("DepartmentKey is not unique.")

        if not self.df["department_code"].is_unique:
            raise ValueError("DepartmentCode is not unique.")

        logger.info("Validation successful.")

    def load(self):

        logger.info("Loading Dim_Department into PostgreSQL...")

        with engine.begin() as connection:

            connection.execute(
                text(
                    f"TRUNCATE TABLE {settings.DB_SCHEMA}.dim_department;"
                )
            )

        self.df.to_sql(
            name="dim_department",
            schema=settings.DB_SCHEMA,
            con=engine,
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

    generator = DimDepartmentGenerator()
    generator.run()