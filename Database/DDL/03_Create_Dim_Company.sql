-- ============================================================================
-- Enterprise Financial Analytics Platform (EFAP)
-- ----------------------------------------------------------------------------
-- Object          : dim_company.sql
-- Object Type     : Dimension Table
-- Layer           : Data Warehouse
-- Version         : 1.0.0
-- Status          : Implemented
-- ----------------------------------------------------------------------------
-- Description:
-- Company dimension.
-- One row represents one legal entity.
-- ============================================================================
CREATE TABLE IF NOT EXISTS warehouse.dim_company (
    company_key INTEGER PRIMARY KEY,
    company_code VARCHAR(20) NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    country_code CHAR(2) NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    currency_code CHAR(3) NOT NULL,
    business_unit VARCHAR(100),
    legal_form VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_dim_company_code ON warehouse.dim_company(company_code);