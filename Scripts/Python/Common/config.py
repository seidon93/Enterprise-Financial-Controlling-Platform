"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
Configuration
===============================================================================
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    # =========================================================================
    # Database
    # =========================================================================
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "EFAP")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_SCHEMA: str = os.getenv("DB_SCHEMA", "warehouse")

    # =========================================================================
    # Calendar
    # =========================================================================
    CALENDAR_START_YEAR: int = 2020
    CALENDAR_END_YEAR: int = 2035
    FISCAL_YEAR_START_MONTH: int = 1

settings = Settings()