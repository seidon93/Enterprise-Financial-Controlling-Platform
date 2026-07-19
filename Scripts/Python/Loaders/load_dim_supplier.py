"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : load_dim_supplier.py
Object Type     : Dimension Loader
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Loads Dim_Supplier into PostgreSQL.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd

from common.database import db


def load_dim_supplier() -> None:
    """
    Loads supplier dimension into PostgreSQL.
    """

    csv_path = (
        Path(__file__).resolve().parent.parent.parent
        / "Data"
        / "dim_supplier.csv"
    )

    df = pd.read_csv(csv_path)

    sql = """
        INSERT INTO warehouse.dim_supplier
        (
            supplier_code,
            supplier_name,
            country_code,
            city,
            payment_terms,
            vat_number,
            active
        )
        VALUES
        (
            %(supplier_code)s,
            %(supplier_name)s,
            %(country_code)s,
            %(city)s,
            %(payment_terms)s,
            %(vat_number)s,
            %(active)s
        )
        ON CONFLICT (supplier_code)
        DO UPDATE SET

            supplier_name = EXCLUDED.supplier_name,
            country_code = EXCLUDED.country_code,
            city = EXCLUDED.city,
            payment_terms = EXCLUDED.payment_terms,
            vat_number = EXCLUDED.vat_number,
            active = EXCLUDED.active;
    """

    with db.connect() as conn:

        with conn.cursor() as cur:

            for row in df.to_dict("records"):

                cur.execute(sql, row)

        conn.commit()

    print(f"Loaded {len(df):,} suppliers.")


if __name__ == "__main__":
    load_dim_supplier()