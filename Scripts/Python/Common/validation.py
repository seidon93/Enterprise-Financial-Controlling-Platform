"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : validation.py
Object Type     : Validation Utilities
Layer           : Common
Version         : 1.0.0
===============================================================================
"""

from __future__ import annotations

import pandas as pd


def validate_not_empty(df: pd.DataFrame) -> None:
    """Raise an error if DataFrame is empty."""

    if df.empty:
        raise ValueError("DataFrame is empty.")


def validate_unique(df: pd.DataFrame, column: str) -> None:
    """Raise an error if values in a column are not unique."""

    if not df[column].is_unique:
        raise ValueError(f"Column '{column}' contains duplicate values.")


def validate_not_null(df: pd.DataFrame, column: str) -> None:
    """Raise an error if a column contains NULL values."""

    if df[column].isnull().any():
        raise ValueError(f"Column '{column}' contains NULL values.")