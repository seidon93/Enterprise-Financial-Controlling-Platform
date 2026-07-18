"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : load_dim_customer.py
Object Type     : Dimension Loader
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Loads Dim_Customer into PostgreSQL.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd

from common.database import db


def load_dim_customer() -> None:
    """
    Loads customer dimension into PostgreSQL.
    """

    csv_path = (
        Path(__file__).resolve().parent.parent.parent
        / "Data"
        / "dim_customer.csv"
    )

    df = pd.read_csv(csv_path)

    sql = """
        INSERT INTO warehouse.dim_customer
        (
            customer_key,
            customer_code,
            customer_name,
            customer_type,
            country_code,
            city,
            industry,
            payment_terms,
            credit_limit,
            risk_category,
            active_from,
            active_to,
            is_active
        )
        VALUES
        (
            %(customer_key)s,
            %(customer_code)s,
            %(customer_name)s,
            %(customer_type)s,
            %(country_code)s,
            %(city)s,
            %(industry)s,
            %(payment_terms)s,
            %(credit_limit)s,
            %(risk_category)s,
            %(active_from)s,
            %(active_to)s,
            %(is_active)s
        )
        ON CONFLICT (customer_key)
        DO UPDATE SET

            customer_code = EXCLUDED.customer_code,
            customer_name = EXCLUDED.customer_name,
            customer_type = EXCLUDED.customer_type,
            country_code = EXCLUDED.country_code,
            city = EXCLUDED.city,
            industry = EXCLUDED.industry,
            payment_terms = EXCLUDED.payment_terms,
            credit_limit = EXCLUDED.credit_limit,
            risk_category = EXCLUDED.risk_category,
            active_from = EXCLUDED.active_from,
            active_to = EXCLUDED.active_to,
            is_active = EXCLUDED.is_active;
    """

    with db.connect() as conn:

        with conn.cursor() as cur:

            for row in df.to_dict("records"):

                cur.execute(sql, row)

        conn.commit()

    print(f"Loaded {len(df):,} customers.")


if __name__ == "__main__":
    load_dim_customer()