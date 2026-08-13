"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : customer_provider.py
Object Type     : Customer Provider
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Provides enterprise customer master data.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import random
from decimal import Decimal
from datetime import date

from domain.customer import Customer


class CustomerProvider:
    """
    Provides enterprise customer master data.
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

        self.industries = [
            "Manufacturing",
            "Retail",
            "Automotive",
            "Healthcare",
            "IT Services",
            "Construction",
            "Logistics",
            "Energy",
        ]

        self.customer_types = [
            "Corporate",
            "SME",
            "Government",
        ]

        self.risk_categories = [
            "LOW",
            "MEDIUM",
            "HIGH",
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

    def create_customer(
        self,
        customer_id: int,
    ) -> Customer:
        """
        Creates one enterprise customer.
        """

        return Customer(
            customer_code=f"CUST{customer_id:06d}",
            customer_name=f"Customer {customer_id:06d}",

            customer_type=self.random.choice(
                self.customer_types
            ),

            country_code=self.random.choice(
                self.countries
            ),

            city=self.random.choice(
                self.cities
            ),

            industry=self.random.choice(
                self.industries
            ),

            payment_terms=self.random.choice(
                [14, 30, 45, 60]
            ),

            credit_limit=Decimal(
                str(
                    self.random.randint(
                        50_000,
                        5_000_000,
                    )
                )
            ),

            risk_category=self.random.choice(
                self.risk_categories
            ),

            active_from=date(
                2020,
                1,
                1,
            ),

            active_to=date(
                2035,
                12,
                31,
            ),

            is_active=True,
        )

    def random_customer(self) -> Customer:
        """
        Returns a random customer.
        """

        customer_id = self.random.randint(1, 10_000)
        return self.create_customer(customer_id)

