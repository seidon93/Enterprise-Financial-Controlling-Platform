"""
Run all DDL scripts against the PostgreSQL database in order.
"""

import sys
from pathlib import Path

# Add Scripts to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "Scripts"))

from common.config import settings
import psycopg2

DDL_DIR = Path(__file__).resolve().parent / "Database"

# Order matters: schemas first, then dimensions, then fact table
DDL_FILES = [
    DDL_DIR / "01_Create_Schemas.sql",
    DDL_DIR / "DDL" / "02_Create_Dim_Date.sql",
    DDL_DIR / "DDL" / "03_Create_Dim_Company.sql",
    DDL_DIR / "DDL" / "04_Create_Dim_Account.sql",
    DDL_DIR / "DDL" / "05_Create_Dim_Cost_Center.sql",
    DDL_DIR / "DDL" / "06_Create_Dim_Department.sql",
    DDL_DIR / "DDL" / "07_Create_Dim_Currency.sql",
    DDL_DIR / "DDL" / "08_Create_Fact_GL.sql",
    DDL_DIR / "DDL" / "10_Create__Dim_Customer.sql",
    DDL_DIR / "DDL" / "11_Create_Dim_Supplier.sql",
    DDL_DIR / "DDL" / "12_Create_Dim_Product.sql",
    DDL_DIR / "DDL" / "13_Create_Dim_Asset.sql",
]


def main():
    conn = psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )
    conn.autocommit = True

    with conn.cursor() as cur:
        for sql_file in DDL_FILES:
            if not sql_file.exists():
                print(f"  SKIP (not found): {sql_file.name}")
                continue
            print(f"  Running: {sql_file.name} ... ", end="")
            sql = sql_file.read_text(encoding="utf-8")
            try:
                cur.execute(sql)
                print("OK")
            except Exception as e:
                print(f"ERROR: {e}")

    conn.close()
    print("\nDone. All DDL scripts executed.")


if __name__ == "__main__":
    main()
