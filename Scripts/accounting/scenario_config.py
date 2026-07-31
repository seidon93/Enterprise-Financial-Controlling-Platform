"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : scenario_config.py
Object Type     : Scenario Configuration
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Central configuration for enterprise data generation scenarios.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dataclasses import dataclass, field

from accounting.load_mode import LoadMode


@dataclass(slots=True)
class ScenarioConfig:
    """
    Global configuration for data generation.
    """

    # -------------------------------------------------------------------------
    # Load Mode
    # -------------------------------------------------------------------------

    load_mode: LoadMode = LoadMode.BANK_ONLY

    # -------------------------------------------------------------------------
    # Time Period
    # -------------------------------------------------------------------------

    start_year: int = 2021
    end_year: int = 2025

    # -------------------------------------------------------------------------
    # Companies
    # -------------------------------------------------------------------------

    companies: list[str] = field(
        default_factory=lambda: [
            "CZ001",
            "SK001",
            "DE001",
            "AT001",
            "PL001",
        ]
    )

    # -------------------------------------------------------------------------
    # Document Volumes
    # -------------------------------------------------------------------------

    sales_documents: int = 45_000
    vendor_documents: int = 30_000
    customer_payments: int = 40_000
    bank_transactions: int = 70_000
    inventory_transactions: int = 100_000
    payroll_documents: int = 7_000
    asset_transactions: int = 3_000
    journal_entries: int = 20_000
    supplier_payments: int = 30_000
    closing_documents: int = 5_000

    # -------------------------------------------------------------------------
    # Random Seed
    # -------------------------------------------------------------------------

    random_seed: int = 42

    # -------------------------------------------------------------------------
    # Batch Size
    # -------------------------------------------------------------------------

    batch_size: int = 5_000