import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "Scripts"))

from common.database import db

c = db.connect()
cur = c.cursor()
cur.execute("SELECT document_number, line_number, account_key, debit_amount, credit_amount, amount_local, description, asset_key, customer_key, supplier_key FROM warehouse.fact_gl WHERE document_number='FA-2024-000111' ORDER BY line_number")
rows = cur.fetchall()
for r in rows:
    print(r)
cur.close()
c.close()
