"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : generate_dim_customer.py
Object Type     : Dimension Generator
Layer           : Data Generation
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates Dim_Customer dimension.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd

from domain.customer_provider import CustomerProvider


def generate_dim_customer(
    customers: int = 10000,
) -> pd.DataFrame:
    """
    Generate customer dimension.
    """

    provider = CustomerProvider()

    rows = []

    for customer_id in range(1, customers + 1):

        customer = provider.create_customer(
            customer_id
        )

        rows.append(
            {
                "customer_key": customer_id,
                "customer_code": customer.customer_code,
                "customer_name": customer.customer_name,
                "customer_type": customer.customer_type,
                "country_code": customer.country_code,
                "city": customer.city,
                "industry": customer.industry,
                "payment_terms": customer.payment_terms,
                "credit_limit": float(
                    customer.credit_limit
                ),
                "risk_category": customer.risk_category,
                "active_from": customer.active_from,
                "active_to": customer.active_to,
                "is_active": customer.is_active,
            }
        )

    return pd.DataFrame(rows)


if __name__ == "__main__":

    df = generate_dim_customer(
        customers=10000
    )

    output = (
        Path(__file__).resolve().parent.parent.parent
        / "Data"
        / "dim_customer.csv"
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        output,
        index=False,
        encoding="utf-8",
    )

    print(
        f"Generated {len(df):,} customers"
    )

    print(
        f"Output: {output}"
    )