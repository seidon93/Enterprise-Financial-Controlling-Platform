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

from decimal import Decimal

import pytest


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