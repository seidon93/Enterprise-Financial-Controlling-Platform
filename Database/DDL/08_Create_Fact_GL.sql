-- ============================================================================
-- Enterprise Financial Analytics Platform (EFAP)
-- ----------------------------------------------------------------------------
-- Object          : 08_Create_Fact_GL.sql
-- Object Type     : Fact Table
-- Layer           : Data Warehouse
-- Version         : 1.0.0
-- Status          : Development
-- ----------------------------------------------------------------------------
-- Description:
-- Creates the General Ledger Fact table.
-- Grain:
-- One record = One accounting journal line.
-- ============================================================================
CREATE TABLE IF NOT EXISTS warehouse.fact_gl (
    -- =====================================================================
    -- Primary Key
    -- =====================================================================
    gl_entry_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY -- =====================================================================
    -- Document Information
    -- =====================================================================
    document_number VARCHAR(30) NOT NULL,
    line_number INTEGER NOT NULL,
    document_type VARCHAR(20) NOT NULL,
    -- =====================================================================
    -- Date Dimensions
    -- =====================================================================
    posting_date_key INTEGER NOT NULL,
    document_date_key INTEGER NOT NULL,
    due_date_key INTEGER NOT NULL,
    -- =====================================================================
    -- Dimension Keys
    -- =====================================================================
    company_key INTEGER NOT NULL,
    account_key INTEGER NOT NULL,
    cost_center_key INTEGER NOT NULL,
    department_key INTEGER NOT NULL,
    currency_key INTEGER NOT NULL,
    -- =====================================================================
    -- Measures
    -- =====================================================================
    debit_amount NUMERIC(18, 2) NOT NULL DEFAULT 0,
    credit_amount NUMERIC(18, 2) NOT NULL DEFAULT 0,
    amount_local NUMERIC(18, 2) NOT NULL,
    quantity NUMERIC(18, 3) DEFAULT 1,
    -- =====================================================================
    -- Business Attributes
    -- =====================================================================
    description VARCHAR(255),
    source_system VARCHAR(50) NOT NULL,
    -- =====================================================================
    -- Audit Columns
    -- =====================================================================
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    batch_id VARCHAR(50),
    -- =====================================================================
    -- Constraints
    -- =====================================================================
    CONSTRAINT uq_fact_gl_document_line UNIQUE (document_number, line_number),
    CONSTRAINT chk_debit_positive CHECK (debit_amount >= 0),
    CONSTRAINT chk_credit_positive CHECK (credit_amount >= 0)
);
-- ============================================================================
-- Foreign Keys
-- ============================================================================
ALTER TABLE warehouse.fact_gl
ADD CONSTRAINT fk_fact_gl_posting_date FOREIGN KEY (posting_date_key) REFERENCES warehouse.dim_date(date_key);
ALTER TABLE warehouse.fact_gl
ADD CONSTRAINT fk_fact_gl_document_date FOREIGN KEY (document_date_key) REFERENCES warehouse.dim_date(date_key);
ALTER TABLE warehouse.fact_gl
ADD CONSTRAINT fk_fact_gl_due_date FOREIGN KEY (due_date_key) REFERENCES warehouse.dim_date(date_key);
ALTER TABLE warehouse.fact_gl
ADD CONSTRAINT fk_fact_gl_company FOREIGN KEY (company_key) REFERENCES warehouse.dim_company(company_key);
ALTER TABLE warehouse.fact_gl
ADD CONSTRAINT fk_fact_gl_account FOREIGN KEY (account_key) REFERENCES warehouse.dim_account(account_key);
ALTER TABLE warehouse.fact_gl
ADD CONSTRAINT fk_fact_gl_cost_center FOREIGN KEY (cost_center_key) REFERENCES warehouse.dim_cost_center(cost_center_key);
ALTER TABLE warehouse.fact_gl
ADD CONSTRAINT fk_fact_gl_department FOREIGN KEY (department_key) REFERENCES warehouse.dim_department(department_key);
ALTER TABLE warehouse.fact_gl
ADD CONSTRAINT fk_fact_gl_currency FOREIGN KEY (currency_key) REFERENCES warehouse.dim_currency(currency_key);
-- ============================================================================
-- Indexes
-- ============================================================================
CREATE INDEX IF NOT EXISTS ix_fact_gl_posting_date ON warehouse.fact_gl(posting_date_key);
CREATE INDEX IF NOT EXISTS ix_fact_gl_account ON warehouse.fact_gl(account_key);
CREATE INDEX IF NOT EXISTS ix_fact_gl_company ON warehouse.fact_gl(company_key);
CREATE INDEX IF NOT EXISTS ix_fact_gl_cost_center ON warehouse.fact_gl(cost_center_key);
CREATE INDEX IF NOT EXISTS ix_fact_gl_department ON warehouse.fact_gl(department_key);
CREATE INDEX IF NOT EXISTS ix_fact_gl_currency ON warehouse.fact_gl(currency_key);
CREATE INDEX IF NOT EXISTS ix_fact_gl_document ON warehouse.fact_gl(document_number);