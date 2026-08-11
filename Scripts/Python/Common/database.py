"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
Database Connection
===============================================================================
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine
from common.config import settings, Settings

app_settings: Settings = settings

connection_string = (
    f"postgresql+psycopg2://"
    f"{app_settings.DB_USER}:{app_settings.DB_PASSWORD}"
    f"@{app_settings.DB_HOST}:{app_settings.DB_PORT}/{app_settings.DB_NAME}"
)

engine = create_engine(connection_string)