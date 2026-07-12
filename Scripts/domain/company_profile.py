"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : company_profile.py
Object Type     : Company Profile
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Defines business characteristics of EFAP legal entities.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CompanyProfile:
    """
    Business profile of one legal entity.
    """

    company_code: str

    currency_code: str

    growth_factor: float

    sales_weight: float

    active_from: int

    active_to: int