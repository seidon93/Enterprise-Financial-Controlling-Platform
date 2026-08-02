"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : conftest.py
Object Type     : Pytest Configuration
Layer           : Tests
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Shared pytest fixtures.
===============================================================================
"""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Make the Scripts directory importable so tests can use
# ``from accounting.models import ...`` etc.
# ---------------------------------------------------------------------------
_SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent / "Scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)


@pytest.fixture
def amount() -> Decimal:
    return Decimal("1000.00")


@pytest.fixture
def currency() -> str:
    return "CZK"


@pytest.fixture
def company() -> str:
    return "CZ01"


@pytest.fixture
def cost_center() -> str:
    return "1000"


@pytest.fixture
def department() -> str:
    return "FIN"