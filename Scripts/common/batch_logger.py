"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : batch_logger.py
Object Type     : Batch Logger
Layer           : Common
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Writes ETL batch execution history into warehouse.etl_batch_history.
===============================================================================
"""

from __future__ import annotations

from common.database import db


class BatchLogger:

    @staticmethod
    def start_batch(
        batch,
        load_mode: str,
    ) -> None:

        with db.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO warehouse.etl_batch_history
                (
                    batch_id,
                    load_mode,
                    started_at,
                    status,
                    rows_inserted
                )
                VALUES
                (
                    %(batch_id)s,
                    %(load_mode)s,
                    %(started_at)s,
                    'RUNNING',
                    0
                )
                """,
                {
                    "batch_id": batch.batch_id,
                    "load_mode": load_mode,
                    "started_at": batch.created_at,
                },
            )

    @staticmethod
    def finish_batch(
        batch,
        rows_inserted: int,
        status: str = "SUCCESS",
        message: str | None = None,
    ) -> None:

        with db.cursor() as cursor:

            cursor.execute(
                """
                UPDATE warehouse.etl_batch_history
                SET
                    finished_at = NOW(),
                    status = %(status)s,
                    rows_inserted = %(rows)s,
                    message = %(message)s
                WHERE batch_id = %(batch_id)s
                """,
                {
                    "status": status,
                    "rows": rows_inserted,
                    "message": message,
                    "batch_id": batch.batch_id,
                },
            )