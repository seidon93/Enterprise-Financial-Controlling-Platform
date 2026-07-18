"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : loader.py
Object Type     : Fact GL Loader
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
from decimal import Decimal

from accounting.dimension_mapper import DimensionMapper
from accounting.models import JournalEntry
from common.batch_context import BatchContext
from common.database import DatabaseManager

logger = logging.getLogger(__name__)


class FactGLLoader:
    """
    Loads JournalEntry objects into warehouse.fact_gl.
    """

    INSERT_SQL = """
    INSERT INTO warehouse.fact_gl
    (
        document_number,
        line_number,
        document_type,
        posting_date_key,
        document_date_key,
        due_date_key,
        company_key,
        account_key,
        cost_center_key,
        department_key,
        currency_key,
        customer_key,
        debit_amount,
        credit_amount,
        amount_local,
        quantity,
        description,
        source_system,
        created_at,
        batch_id
    )
    VALUES
    (
        %(document_number)s,
        %(line_number)s,
        %(document_type)s,
        %(posting_date_key)s,
        %(document_date_key)s,
        %(due_date_key)s,
        %(company_key)s,
        %(account_key)s,
        %(cost_center_key)s,
        %(department_key)s,
        %(currency_key)s,
        %(customer_key)s,
        %(debit_amount)s,
        %(credit_amount)s,
        %(amount_local)s,
        %(quantity)s,
        %(description)s,
        %(source_system)s,
        %(created_at)s,
        %(batch_id)s,
    )
    ON CONFLICT (document_number, line_number)
    DO UPDATE SET
        document_type     = EXCLUDED.document_type,
        posting_date_key  = EXCLUDED.posting_date_key,
        document_date_key = EXCLUDED.document_date_key,
        due_date_key      = EXCLUDED.due_date_key,
        company_key       = EXCLUDED.company_key,
        account_key       = EXCLUDED.account_key,
        cost_center_key   = EXCLUDED.cost_center_key,
        department_key    = EXCLUDED.department_key,
        currency_key      = EXCLUDED.currency_key,
        debit_amount      = EXCLUDED.debit_amount,
        credit_amount     = EXCLUDED.credit_amount,
        amount_local      = EXCLUDED.amount_local,
        quantity          = EXCLUDED.quantity,
        description       = EXCLUDED.description,
        source_system     = EXCLUDED.source_system,
        created_at        = EXCLUDED.created_at,
        batch_id          = EXCLUDED.batch_id
    """

    def __init__(
        self,
        database: DatabaseManager,
        mapper: DimensionMapper,
    ) -> None:

        self.database = database
        self.mapper = mapper

    def load(
        self,
        entry: JournalEntry,
        batch: BatchContext,
    ) -> int:
        """
        Load JournalEntry into warehouse.fact_gl.

        Returns
        -------
        int
            Number of inserted rows.
        """

        inserted_rows = 0

        with self.database.cursor() as cursor:

            for line in entry.lines:

                cursor.execute(
                    self.INSERT_SQL,
                    {
                        "document_number": entry.document.document_number,
                        "line_number": line.line_number,
                        "document_type": entry.document.document_type,

                        "posting_date_key": self.mapper.date_key(
                            entry.document.posting_date
                        ),
                        "document_date_key": self.mapper.date_key(
                            entry.document.document_date
                        ),
                        "due_date_key": self.mapper.date_key(
                            entry.document.due_date
                        ),

                        "company_key": self.mapper.company_key(
                            line.company_code
                        ),
                        "account_key": self.mapper.account_key(
                            line.account_number
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
                        "customer_key": self.mapper.customer_key(
                            line.customer_code
                        ),

                        "debit_amount": line.debit_amount,
                        "credit_amount": line.credit_amount,
                        "amount_local": line.amount_local,

                        "quantity": Decimal("1.00"),

                        "description": line.description,

                        "source_system": batch.source_system,
                        "created_at": batch.created_at,
                        "batch_id": batch.batch_id,
                    },
                )

                inserted_rows += 1
                logger.debug(
                    "Inserted line %s",
                    line.line_number,
                )

        logger.info(
            "Inserted %s rows for document %s",
            inserted_rows,
            entry.document.document_number,
        )

        return inserted_rows