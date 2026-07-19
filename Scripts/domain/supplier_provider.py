"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : supplier_provider.py
Object Type     : Supplier Provider
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Provides enterprise supplier master data.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import random

from domain.supplier import Supplier


class SupplierProvider:
    """
    Provides enterprise supplier master data.
    """

    def __init__(
        self,
        seed: int = 42,
    ) -> None:

        self.random = random.Random(seed)

        self.countries = [
            "CZ",
            "SK",
            "DE",
            "AT",
            "PL",
        ]

        self.cities = [
            "Prague",
            "Brno",
            "Ostrava",
            "Bratislava",
            "Vienna",
            "Warsaw",
            "Berlin",
            "Munich",
        ]

    def create_supplier(
        self,
        supplier_id: int,
    ) -> Supplier:
        """
        Creates one enterprise supplier.
        """

        country = self.random.choice(self.countries)

        return Supplier(
            supplier_code=f"SUP{supplier_id:06d}",
            supplier_name=f"Supplier {supplier_id:06d}",
            country_code=country,
            city=self.random.choice(self.cities),
            payment_terms=self.random.choice([14, 30, 45, 60]),
            vat_number=f"{country}{100000000 + supplier_id}",
            active=True,
        )

    def random_supplier(self) -> Supplier:
        """
        Returns a random supplier.
        """

        supplier_id = self.random.randint(1, 10_000)
        return self.create_supplier(supplier_id)