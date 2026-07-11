-- ============================================================================
-- Enterprise Financial Analytics Platform (EFAP)
-- ----------------------------------------------------------------------------
-- Object          : 07_Create_Dim_Currency.sql
-- Object Type     : Dimension Table
-- Layer           : Data Warehouse
-- Version         : 1.0.0
-- Status          : Development
-- ----------------------------------------------------------------------------
-- Description:
-- Creates the Currency Dimension.
-- ============================================================================
CREATE TABLE IF NOT EXISTS warehouse.dim_currency (
    currency_key INTEGER PRIMARY KEY,
    currency_code VARCHAR(3) NOT NULL,
    currency_name VARCHAR(100) NOT NULL,
    currency_symbol VARCHAR(10),
    country VARCHAR(100),
    iso_numeric INTEGER,
    is_reporting_currency BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_dim_currency_code ON warehouse.dim_currency(currency_code);