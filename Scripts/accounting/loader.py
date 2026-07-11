"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : loader.py
Object Type     : Fact_GL Loader
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Loads validated JournalEntry objects into warehouse.fact_gl.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging

from accounting.dimension_mapper import DimensionMapper
from accounting.models import JournalEntry
from common.database import DatabaseManager

logger = logging.getLogger(__name__)


class FactGLLoader:
    """
    Loads JournalEntry objects into warehouse.fact_gl.
    """

    def __init__(
        self,
        database: DatabaseManager,
        mapper: DimensionMapper,
    ) -> None:

        self.database = database
        self.mapper = mapper

    def load(self, entry: JournalEntry) -> int:
        """
        Load one JournalEntry into Fact_GL.

        Returns
        -------
        int
            Number of inserted rows.
        """

        sql = """
        INSERT INTO warehouse.fact_gl
        (
            date_key,
            account_key,
            company_key,
            cost_center_key,
            department_key,
            currency_key,
            document_number,
            line_number,
            debit_amount,
            credit_amount,
            amount_local,
            description
        )
        VALUES
        (
            %(date_key)s,
            %(account_key)s,
            %(company_key)s,
            %(cost_center_key)s,
            %(department_key)s,
            %(currency_key)s,
            %(document_number)s,
            %(line_number)s,
            %(debit_amount)s,
            %(credit_amount)s,
            %(amount_local)s,
            %(description)s
        )
        """

        inserted_rows = 0

        with self.database.cursor() as cursor:

            for line in entry.lines:

                cursor.execute(
                    sql,
                    {
                        "date_key": self.mapper.date_key(
                            entry.document.posting_date
                        ),
                        "account_key": self.mapper.account_key(
                            line.account_number
                        ),
                        "company_key": self.mapper.company_key(
                            line.company_code
                        ),
                        "cost_center_key": self.mapper.cost_center_key(
                            line.cost_center_code
                        ),
                        "department_key": self.mapper.department_key(
                            line.department_code
                        ),
                        "currency_key": self.mapper.currency_key(
                            line.currency_code
                        ),
                        "document_number": entry.document.document_number,
                        "line_number": line.line_number,
                        "debit_amount": line.debit_amount,
                        "credit_amount": line.credit_amount,
                        "amount_local": line.amount_local,
                        "description": line.description,
                    },
                )

                inserted_rows += 1

        logger.info(
            "Loaded %s rows for document %s",
            inserted_rows,
            entry.document.document_number,
        )

        return inserted_rows