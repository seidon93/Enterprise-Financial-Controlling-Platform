"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : asset_provider.py
Object Type     : Asset Provider
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Provides enterprise fixed asset master data.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import random

from datetime import date
from decimal import Decimal

from domain.asset import Asset
from domain.supplier_provider import SupplierProvider
from domain.business_data_provider import BusinessDataProvider


class AssetProvider:
    """
    Provides enterprise fixed asset master data.
    """

    def __init__(
        self,
        seed: int = 42,
    ) -> None:

        self.random = random.Random(seed)

        self.supplier_provider = SupplierProvider(seed)
        self.business_provider = BusinessDataProvider(seed)

        self.asset_categories = {
            "Buildings": {
                "life": 360,
                "price": (10_000_000, 100_000_000),
                "items": [
                    "Head Office",
                    "Production Hall",
                    "Warehouse",
                    "Administration Building",
                ],
            },
            "Production Equipment": {
                "life": 96,
                "price": (300_000, 5_000_000),
                "items": [
                    "Packaging Line",
                    "Assembly Line",
                    "Robot Cell",
                ],
            },
            "Machinery": {
                "life": 120,
                "price": (500_000, 8_000_000),
                "items": [
                    "CNC Machine",
                    "Hydraulic Press",
                    "Industrial Lathe",
                    "Forklift",
                ],
            },
            "Vehicles": {
                "life": 60,
                "price": (400_000, 2_000_000),
                "items": [
                    "Škoda Octavia",
                    "Ford Transit",
                    "Toyota Proace",
                    "VW Transporter",
                ],
            },
            "IT Equipment": {
                "life": 36,
                "price": (25_000, 150_000),
                "items": [
                    "Dell Latitude",
                    "HP EliteBook",
                    "Cisco Switch",
                    "Synology NAS",
                    "VMware Server",
                ],
            },
            "Office Equipment": {
                "life": 48,
                "price": (5_000, 80_000),
                "items": [
                    "Printer",
                    "Scanner",
                    "Conference Display",
                ],
            },
            "Furniture": {
                "life": 60,
                "price": (10_000, 200_000),
                "items": [
                    "Office Desk",
                    "Meeting Table",
                    "Office Cabinet",
                ],
            },
            "Software": {
                "life": 36,
                "price": (50_000, 3_000_000),
                "items": [
                    "Microsoft Dynamics 365",
                    "Power BI Premium",
                    "SQL Server Enterprise",
                    "Microsoft 365",
                ],
            },
        }

    def create_asset(
        self,
        asset_id: int,
    ) -> Asset:
        """
        Creates one enterprise asset.
        """

        category = self.random.choice(
            list(self.asset_categories.keys())
        )

        metadata = self.asset_categories[category]

        supplier = self.supplier_provider.random_supplier()

        company = self.business_provider.random_company()

        acquisition_cost = Decimal(
            str(
                self.random.randint(
                    metadata["price"][0],
                    metadata["price"][1],
                )
            )
        )

        return Asset(

            asset_code=f"AST{asset_id:06d}",

            asset_name=self.random.choice(
                metadata["items"]
            ),

            asset_category=category,

            company_code=company.company_code,

            supplier_code=supplier.supplier_code,

            acquisition_date=date(
                self.random.randint(2021, 2025),
                self.random.randint(1, 12),
                self.random.randint(1, 28),
            ),

            acquisition_cost=acquisition_cost,

            useful_life_months=metadata["life"],

            depreciation_method="STRAIGHT_LINE",

            salvage_value=Decimal("0.00"),

            currency_code=company.currency_code,

            cost_center_code=self.business_provider.random_cost_center(),

            department_code=self.business_provider.random_department(),

            is_active=True,
        )

    def random_asset(self) -> Asset:
        """
        Returns a random enterprise asset.
        """

        asset_id = self.random.randint(1, 100_000)

        return self.create_asset(asset_id)