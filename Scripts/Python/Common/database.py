"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
Database Connection
===============================================================================
"""

from sqlalchemy import create_engine

from common.config import settings


connection_string = (
    f"postgresql+psycopg2://"
    f"{settings.DB_USER}:"
    f"{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:"
    f"{settings.DB_PORT}/"
    f"{settings.DB_NAME}"
)

engine = create_engine(connection_string)