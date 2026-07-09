"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
Database Connection
===============================================================================
"""

import sys
from pathlib import Path

# Add Scripts/Python to path so 'common' package is discoverable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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