"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : variance_rule.py
Object Type     : Domain Model
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Defines evaluation rules for Budget vs Actual variance.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from Scripts.domain.kpi_type import KPIType


@dataclass(slots=True, frozen=True)
class VarianceRule:

    account_number: str

    kpi_type: KPIType

    favorable_if_higher: bool