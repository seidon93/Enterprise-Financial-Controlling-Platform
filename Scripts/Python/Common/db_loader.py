"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : db_loader.py
Object Type     : Database Utilities
Layer           : Common
Version         : 1.0.0
===============================================================================
"""

from __future__ import annotations

import pandas as pd

from sqlalchemy import text

from common.database import engine
from common.config import settings


def truncate_table(table_name: str) -> None:
    """
    Truncate a database table.
    """

    with engine.begin() as connection:

        connection.execute(
            text(
                f"TRUNCATE TABLE {settings.DB_SCHEMA}.{table_name} CASCADE;"
            )
        )


def load_dataframe(
    df: pd.DataFrame,
    table_name: str,
) -> None:
    """
    Load a DataFrame into PostgreSQL.
    """

    with engine.begin() as connection:
        df.to_sql(
            name=table_name,
            schema=settings.DB_SCHEMA,
            con=connection,  # type: ignore
            if_exists="append",
            index=False,
            method="multi",
        )


def replace_table(
    df: pd.DataFrame,
    table_name: str,
) -> None:
    """
    Replace table content with DataFrame.
    """

    truncate_table(table_name)

    load_dataframe(
        df=df,
        table_name=table_name,
    )