"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : database.py
Object Type     : Database Connection Manager
Layer           : Common
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Provides a reusable PostgreSQL database connection for all ETL processes.
===============================================================================
"""

from __future__ import annotations

import logging
import sys
from contextlib import contextmanager
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

# Add Scripts to path so 'common' package is discoverable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    PostgreSQL connection manager.
    """

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
    ) -> None:

        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

    def connect(self):
        """
        Create PostgreSQL connection.
        """

        logger.info("Connecting to PostgreSQL...")

        return psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
        )

    @contextmanager
    def cursor(self):
        """
        Context manager for database cursor.
        """

        connection = self.connect()

        try:

            cursor = connection.cursor(cursor_factory=RealDictCursor)

            yield cursor

            connection.commit()

        except Exception:

            connection.rollback()

            logger.exception("Database transaction failed.")

            raise

        finally:

            cursor.close()

            connection.close()

            logger.info("Database connection closed.")


# =============================================================================
# Module-level instance
# =============================================================================

db = DatabaseManager(
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
    user=settings.db_user,
    password=settings.db_password,
)

from sqlalchemy import create_engine

connection_string = (
    f"postgresql+psycopg2://"
    f"{settings.db_user}:"
    f"{settings.db_password}@"
    f"{settings.db_host}:"
    f"{settings.db_port}/"
    f"{settings.db_name}"
)

engine = create_engine(connection_string)