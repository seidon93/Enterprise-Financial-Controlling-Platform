-- ============================================================================
-- Enterprise Financial Analytics Platform (EFAP)
-- ----------------------------------------------------------------------------
-- Object          : dim_account.sql
-- Object Type     : Dimension Table
-- Layer           : Data Warehouse
-- Version         : 1.0.0
-- Status          : Development
-- ----------------------------------------------------------------------------
-- Description:
-- General Ledger Account Dimension.
-- One row represents one General Ledger account.
-- ============================================================================
CREATE TABLE IF NOT EXISTS warehouse.dim_account (
    account_key INTEGER PRIMARY KEY,
    account_number VARCHAR(20) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_type CHAR(1) NOT NULL,
    account_class SMALLINT NOT NULL,
    account_group SMALLINT NOT NULL,
    statement_type VARCHAR(30) NOT NULL,
    reporting_group VARCHAR(100),
    reporting_category VARCHAR(100),
    normal_balance VARCHAR(10),
    is_posting_account BOOLEAN NOT NULL DEFAULT TRUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_dim_account_number ON warehouse.dim_account(account_number);