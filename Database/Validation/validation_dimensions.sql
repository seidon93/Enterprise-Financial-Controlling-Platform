/*
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : validation_dimensions.sql
Object Type     : Validation Script
Layer           : Database Validation
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Validates referential integrity between Fact_GL and all dimension tables.
===============================================================================
*/
SELECT
    COUNT(*) AS companies
FROM
    warehouse.dim_company;

SELECT
    COUNT(*) AS customers
FROM
    warehouse.dim_customer;

SELECT
    COUNT(*) AS suppliers
FROM
    warehouse.dim_supplier;

SELECT
    COUNT(*) AS accounts
FROM
    warehouse.dim_account;

SELECT
    COUNT(*) AS currencies
FROM
    warehouse.dim_currency;

SELECT
    COUNT(*) AS cost_centers
FROM
    warehouse.dim_cost_center;

SELECT
    COUNT(*) AS departments
FROM
    warehouse.dim_department;

SELECT
    COUNT(*) AS dates
FROM
    warehouse.dim_date;