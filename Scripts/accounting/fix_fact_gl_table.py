"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : fix_fact_gl_table.py
Object Type     : Database Migration / Repair Script
Layer           : Database / Warehouse
Version         : 2.0.0
Status          : Development

Description:
    Recreates warehouse.fact_gl with the complete structure required by
    the accounting loader and controller analytics.

    The table contains transactional accounting data together with the
    sales attributes required for Price × Volume analysis.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent),
)

from common.database import db


DDL = """
DROP TABLE IF EXISTS warehouse.fact_gl CASCADE;

CREATE TABLE warehouse.fact_gl (
    gl_entry_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    document_number VARCHAR(30) NOT NULL,
    line_number INTEGER NOT NULL,
    document_type VARCHAR(20) NOT NULL,

    posting_date_key INTEGER NOT NULL,
    document_date_key INTEGER NOT NULL,
    due_date_key INTEGER NOT NULL,

    company_key INTEGER NOT NULL,
    account_key INTEGER NOT NULL,
    cost_center_key INTEGER NOT NULL,
    department_key INTEGER NOT NULL,
    currency_key INTEGER NOT NULL,

    customer_key INTEGER,
    supplier_key INTEGER,
    asset_key INTEGER,

    debit_amount NUMERIC(18, 2) NOT NULL DEFAULT 0,
    credit_amount NUMERIC(18, 2) NOT NULL DEFAULT 0,
    amount_local NUMERIC(18, 2) NOT NULL,

    quantity NUMERIC(18, 3) DEFAULT 1,
    unit_price NUMERIC(18, 2),
    material_code VARCHAR(50),

    description VARCHAR(255),

    source_system VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    batch_id VARCHAR(50),

    CONSTRAINT uq_fact_gl_document_line
        UNIQUE (document_number, line_number),

    CONSTRAINT chk_debit_positive
        CHECK (debit_amount >= 0),

    CONSTRAINT chk_credit_positive
        CHECK (credit_amount >= 0)
);


ALTER TABLE warehouse.fact_gl
ADD CONSTRAINT fk_fact_gl_posting_date
FOREIGN KEY (posting_date_key)
REFERENCES warehouse.dim_date(date_key);


ALTER TABLE warehouse.fact_gl
ADD CONSTRAINT fk_fact_gl_document_date
FOREIGN KEY (document_date_key)
REFERENCES warehouse.dim_date(date_key);


ALTER TABLE warehouse.fact_gl
ADD CONSTRAINT fk_fact_gl_due_date
FOREIGN KEY (due_date_key)
REFERENCES warehouse.dim_date(date_key);


ALTER TABLE warehouse.fact_gl
ADD CONSTRAINT fk_fact_gl_company
FOREIGN KEY (company_key)
REFERENCES warehouse.dim_company(company_key);


ALTER TABLE warehouse.fact_gl
ADD CONSTRAINT fk_fact_gl_account
FOREIGN KEY (account_key)
REFERENCES warehouse.dim_account(account_key);


ALTER TABLE warehouse.fact_gl
ADD CONSTRAINT fk_fact_gl_cost_center
FOREIGN KEY (cost_center_key)
REFERENCES warehouse.dim_cost_center(cost_center_key);


ALTER TABLE warehouse.fact_gl
ADD CONSTRAINT fk_fact_gl_department
FOREIGN KEY (department_key)
REFERENCES warehouse.dim_department(department_key);


ALTER TABLE warehouse.fact_gl
ADD CONSTRAINT fk_fact_gl_currency
FOREIGN KEY (currency_key)
REFERENCES warehouse.dim_currency(currency_key);


CREATE INDEX IF NOT EXISTS ix_fact_gl_posting_date
    ON warehouse.fact_gl(posting_date_key);

CREATE INDEX IF NOT EXISTS ix_fact_gl_account
    ON warehouse.fact_gl(account_key);

CREATE INDEX IF NOT EXISTS ix_fact_gl_company
    ON warehouse.fact_gl(company_key);

CREATE INDEX IF NOT EXISTS ix_fact_gl_cost_center
    ON warehouse.fact_gl(cost_center_key);

CREATE INDEX IF NOT EXISTS ix_fact_gl_department
    ON warehouse.fact_gl(department_key);

CREATE INDEX IF NOT EXISTS ix_fact_gl_currency
    ON warehouse.fact_gl(currency_key);

CREATE INDEX IF NOT EXISTS ix_fact_gl_document
    ON warehouse.fact_gl(document_number);

CREATE INDEX IF NOT EXISTS ix_fact_gl_material
    ON warehouse.fact_gl(material_code);
"""


def main() -> None:
    print(
        "Dropping and recreating warehouse.fact_gl..."
    )

    with db.cursor() as cursor:
        cursor.execute(DDL)

    print(
        "Done! fact_gl table recreated with complete "
        "accounting and sales attributes."
    )


if __name__ == "__main__":
    main()

