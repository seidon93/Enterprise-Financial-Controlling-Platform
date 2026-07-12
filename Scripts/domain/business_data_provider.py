"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : business_data_provider.py
Object Type     : Business Data Provider
Layer           : Domain
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import random

from domain.company_profile import CompanyProfile


class BusinessDataProvider:
    """
    Provides realistic enterprise business data.
    """

    def __init__(self, seed: int = 42):

        self.random = random.Random(seed)

        self.company_profiles = [

            CompanyProfile(
                company_code="CZ001",
                currency_code="CZK",
                growth_factor=1.10,
                sales_weight=0.45,
                active_from=2021,
                active_to=2035,
            ),

            CompanyProfile(
                company_code="SK001",
                currency_code="EUR",
                growth_factor=1.07,
                sales_weight=0.20,
                active_from=2021,
                active_to=2035,
            ),

            CompanyProfile(
                company_code="DE001",
                currency_code="EUR",
                growth_factor=1.18,
                sales_weight=0.15,
                active_from=2022,
                active_to=2035,
            ),

            CompanyProfile(
                company_code="AT001",
                currency_code="EUR",
                growth_factor=1.05,
                sales_weight=0.10,
                active_from=2023,
                active_to=2035,
            ),

            CompanyProfile(
                company_code="PL001",
                currency_code="PLN",
                growth_factor=1.12,
                sales_weight=0.10,
                active_from=2024,
                active_to=2035,
            ),
        ]

    def random_company(self) -> CompanyProfile:
        """
        Returns one company according to business weights.
        """

        return self.random.choices(
            self.company_profiles,
            weights=[c.sales_weight for c in self.company_profiles],
            k=1,
        )[0]