-- ============================================================================
-- Enterprise Financial Analytics Platform (EFAP)
-- ----------------------------------------------------------------------------
-- Object          : 05_Create_Dim_Cost_Center.sql
-- Object Type     : Dimension Table
-- Layer           : Data Warehouse
-- Version         : 1.0.0
-- Status          : Development
--
-- Description:
-- Creates the Cost Center Dimension.
-- One row represents one Cost Center.
-- ============================================================================
CREATE TABLE IF NOT EXISTS warehouse.dim_cost_center (
    cost_center_key INTEGER PRIMARY KEY,
    cost_center_code VARCHAR(20) NOT NULL,
    cost_center_name VARCHAR(100) NOT NULL,
    parent_cost_center_code VARCHAR(20),
    cost_center_level SMALLINT,
    department_name VARCHAR(100),
    manager_name VARCHAR(100),
    location VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_dim_cost_center_code ON warehouse.dim_cost_center(cost_center_code);