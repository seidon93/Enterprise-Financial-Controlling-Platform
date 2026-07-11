-- ============================================================================
-- Enterprise Financial Analytics Platform (EFAP)
-- ----------------------------------------------------------------------------
-- Object          : 06_Create_Dim_Department.sql
-- Object Type     : Dimension Table
-- Layer           : Data Warehouse
-- Version         : 1.0.0
-- Status          : Development
-- ----------------------------------------------------------------------------
-- Description:
-- Creates the Department Dimension.
-- ============================================================================
CREATE TABLE IF NOT EXISTS warehouse.dim_department (
    department_key INTEGER PRIMARY KEY,
    department_code VARCHAR(20) NOT NULL,
    department_name VARCHAR(100) NOT NULL,
    division_name VARCHAR(100),
    director_name VARCHAR(100),
    location VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_dim_department_code ON warehouse.dim_department(department_code);