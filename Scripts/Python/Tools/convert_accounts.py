"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : convert_accounts.py
Object Type     : Utility
Layer           : Data Preparation
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------

Description:
Converts the Chart of Accounts from Markdown format to CSV.

===============================================================================
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd


# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# =============================================================================
# Paths
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = PROJECT_ROOT / "Data" / "Raw" / "account_chart.md"
OUTPUT_FILE = PROJECT_ROOT / "Data" / "Reference" / "accounts.csv"