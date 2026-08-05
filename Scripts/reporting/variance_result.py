"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : variance_result.py
Object Type     : Domain Model
Layer           : Reporting
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True, frozen=True)
class VarianceResult:
    """
    Budget vs Actual comparison result.
    """
    
    account_code: str

    budget: Decimal

    actual: Decimal

    variance: Decimal

    variance_percent: Decimal

    favorable: bool