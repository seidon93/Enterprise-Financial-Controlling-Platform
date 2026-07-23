/*
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : dim_asset
Object Type     : Dimension Table
Layer           : Data Warehouse
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Enterprise Asset Dimension.
Stores master data for fixed assets.
===============================================================================
*/
CREATE TABLE IF NOT EXISTS warehouse.dim_asset (
    asset_key SERIAL PRIMARY KEY,
    asset_code VARCHAR(30) NOT NULL,
    asset_name VARCHAR(200) NOT NULL,
    asset_class VARCHAR(100),
    asset_group VARCHAR(100),
    company_code VARCHAR(20),
    supplier_code VARCHAR(30),
    currency_code VARCHAR(10),
    acquisition_date DATE,
    capitalization_date DATE,
    depreciation_start_date DATE,
    acquisition_cost NUMERIC(18, 2),
    residual_value NUMERIC(18, 2),
    useful_life_months INTEGER,
    depreciation_method VARCHAR(50),
    cost_center_code VARCHAR(30),
    department_code VARCHAR(30),
    country_code VARCHAR(10),
    city VARCHAR(100),
    location VARCHAR(200),
    vat_rate NUMERIC(5, 2),
    is_active BOOLEAN,
    disposal_date DATE,
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_to TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_dim_asset_code ON warehouse.dim_asset (asset_code);

CREATE INDEX IF NOT EXISTS ix_dim_asset_company ON warehouse.dim_asset (company_code);

CREATE INDEX IF NOT EXISTS ix_dim_asset_supplier ON warehouse.dim_asset (supplier_code);

CREATE INDEX IF NOT EXISTS ix_dim_asset_class ON warehouse.dim_asset (asset_class);

COMMENT ON TABLE warehouse.dim_asset IS 'Enterprise Asset Dimension';