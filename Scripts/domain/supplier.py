"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : supplier.py
Object Type     : Supplier Entity
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Enterprise supplier master data entity.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Supplier:
    """
    Supplier master record.
    """

    supplier_code: str
    supplier_name: str
    country_code: str
    city: str
    payment_terms: int
    vat_number: str
    active: bool = True