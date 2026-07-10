"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : generate_dim_company.py
Object Type     : ETL Generator
Layer           : Data Generation
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------

Description:
Generates the Company dimension and loads it into PostgreSQL.

===============================================================================
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from datetime import date

import pandas as pd
from sqlalchemy import text

import sys
from pathlib import Path

# Add Scripts/Python to the path so 'common' package can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.config import settings
from common.constants import (
    BUSINESS_UNITS,
    LEGAL_FORMS,
    VALID_FROM,
    VALID_TO,
)
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
# Company
# =============================================================================

@dataclass(frozen=True, slots=True)
class Company:

    company_key: int

    company_code: str
    company_name: str

    country_code: str
    country_name: str

    currency_code: str

    business_unit: str

    legal_form: str

    is_active: bool

    valid_from: date
    valid_to: date

# =============================================================================
# Generator
# =============================================================================

class DimCompanyGenerator:

    def __init__(self) -> None:

        self.df: pd.DataFrame = pd.DataFrame()

    # =========================================================================
    # Public API
    # =========================================================================

    def run(self) -> None:

        logger.info("Starting Dim_Company generation...")

        self.generate()

        self.validate()

        self.load()

        logger.info("Dim_Company finished successfully.")

        # =========================================================================
    # Create DataFrame
    # =========================================================================

    def _create_dataframe(self) -> None:

        logger.info("Creating company dataframe...")

        companies = [

            Company(
                company_key=1,
                company_code="CZ001",
                company_name="EFAP Czech Republic s.r.o.",
                country_code="CZ",
                country_name="Czech Republic",
                currency_code="CZK",
                business_unit=BUSINESS_UNITS["CZ"],
                legal_form=LEGAL_FORMS["CZ"],
                is_active=True,
                valid_from=VALID_FROM,
                valid_to=VALID_TO,
            ),

            Company(
                company_key=2,
                company_code="SK001",
                company_name="EFAP Slovakia s.r.o.",
                country_code="SK",
                country_name="Slovakia",
                currency_code="EUR",
                business_unit=BUSINESS_UNITS["SK"],
                legal_form=LEGAL_FORMS["SK"],
                is_active=True,
                valid_from=VALID_FROM,
                valid_to=VALID_TO,
            ),

            Company(
                company_key=3,
                company_code="DE001",
                company_name="EFAP Deutschland GmbH",
                country_code="DE",
                country_name="Germany",
                currency_code="EUR",
                business_unit=BUSINESS_UNITS["DE"],
                legal_form=LEGAL_FORMS["DE"],
                is_active=True,
                valid_from=VALID_FROM,
                valid_to=VALID_TO,
            ),

            Company(
                company_key=4,
                company_code="AT001",
                company_name="EFAP Österreich GmbH",
                country_code="AT",
                country_name="Austria",
                currency_code="EUR",
                business_unit=BUSINESS_UNITS["AT"],
                legal_form=LEGAL_FORMS["AT"],
                is_active=True,
                valid_from=VALID_FROM,
                valid_to=VALID_TO,
            ),

            Company(
                company_key=5,
                company_code="PL001",
                company_name="EFAP Polska Sp. z o.o.",
                country_code="PL",
                country_name="Poland",
                currency_code="PLN",
                business_unit=BUSINESS_UNITS["PL"],
                legal_form=LEGAL_FORMS["PL"],
                is_active=True,
                valid_from=VALID_FROM,
                valid_to=VALID_TO,
            ),

        ]

        self.df = pd.DataFrame(
            [asdict(company) for company in companies]
        )

        logger.info(
            "Created %d companies.",
            len(self.df),
        )

    # =========================================================================
    # Validation
    # =========================================================================

    def _validate_dataframe(self) -> None:

        if self.df.empty:
            raise ValueError("Company dataframe is empty.")

        if not self.df["company_key"].is_unique:
            raise ValueError("company_key must be unique.")

        if not self.df["company_code"].is_unique:
            raise ValueError("company_code must be unique.")

        if self.df.isnull().any().any():
            raise ValueError("Company dataframe contains NULL values.")



    def generate(self) -> pd.DataFrame:

        logger.info("Generating Dim_Company...")

        self._create_dataframe()

        return self.df



    def validate(self) -> None:

        logger.info("Validating Dim_Company...")

        self._validate_dataframe()

        logger.info("Validation successful.")



    def load(self) -> None:

        logger.info("Loading Dim_Company into PostgreSQL...")

        with engine.begin() as connection:

            connection.execute(
                text(
                    f"TRUNCATE TABLE {settings.DB_SCHEMA}.dim_company;"
                )
            )

        self.df.to_sql(
            name="dim_company",
            schema=settings.DB_SCHEMA,
            con=engine,
            if_exists="append",
            index=False,
        )

        logger.info(
            "Loaded %s rows.",
            len(self.df),
        )

# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    generator = DimCompanyGenerator()

    generator.run()