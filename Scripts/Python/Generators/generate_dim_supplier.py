"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : generate_dim_supplier.py
Object Type     : Dimension Generator
Layer           : Data Generation
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates enterprise Supplier dimension.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import csv
import random

from domain.supplier import Supplier


OUTPUT_FILE = (
    Path(__file__).resolve().parents[2]
    / "Data"
    / "dim_supplier.csv"
)

SUPPLIER_COUNT = 5000

random.seed(42)


COUNTRIES = [
    ("CZ", "Prague"),
    ("CZ", "Brno"),
    ("CZ", "Ostrava"),
    ("SK", "Bratislava"),
    ("DE", "Munich"),
    ("DE", "Berlin"),
    ("AT", "Vienna"),
    ("PL", "Warsaw"),
]


PAYMENT_TERMS = [14, 30, 45, 60]


def generate_supplier(index: int) -> Supplier:

    country, city = random.choice(COUNTRIES)

    return Supplier(
        supplier_code=f"SUP{index:06}",
        supplier_name=f"Supplier {index:06}",
        country_code=country,
        city=city,
        payment_terms=random.choice(PAYMENT_TERMS),
        vat_number=f"{country}{100000000 + index}",
        active=True,
    )


def main() -> None:

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    suppliers = [
        generate_supplier(i)
        for i in range(1, SUPPLIER_COUNT + 1)
    ]

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow(
            [
                "supplier_code",
                "supplier_name",
                "country_code",
                "city",
                "payment_terms",
                "vat_number",
                "active",
            ]
        )

        for supplier in suppliers:
            writer.writerow(
                [
                    supplier.supplier_code,
                    supplier.supplier_name,
                    supplier.country_code,
                    supplier.city,
                    supplier.payment_terms,
                    supplier.vat_number,
                    supplier.active,
                ]
            )

    print(f"Generated {SUPPLIER_COUNT:,} suppliers")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()