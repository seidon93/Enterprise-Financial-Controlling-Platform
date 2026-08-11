"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : config.py
Object Type     : Configuration
Layer           : Common
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True, slots=True)
class Settings:
    """Application settings."""

    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "EFAP")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "")
    DB_SCHEMA: str = os.getenv("DB_SCHEMA", "warehouse")
    CALENDAR_START_YEAR: int = 2020
    CALENDAR_END_YEAR: int = 2035
    FISCAL_YEAR_START_MONTH: int = 1


settings = Settings()