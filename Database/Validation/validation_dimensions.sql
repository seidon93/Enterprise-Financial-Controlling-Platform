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
-- ============================================================================
-- Missing Company
-- ============================================================================
SELECT
    f.gl_entry_key,
    f.company_key
FROM
    warehouse.fact_gl f
    LEFT JOIN warehouse.dim_company c ON f.company_key = c.company_key
WHERE
    c.company_key IS NULL;

-- ============================================================================
-- Missing Account
-- ============================================================================
SELECT
    f.gl_entry_key,
    f.account_key
FROM
    warehouse.fact_gl f
    LEFT JOIN warehouse.dim_account a ON f.account_key = a.account_key
WHERE
    a.account_key IS NULL;

-- ============================================================================
-- Missing Cost Center
-- ============================================================================
SELECT
    f.gl_entry_key,
    f.cost_center_key
FROM
    warehouse.fact_gl f
    LEFT JOIN warehouse.dim_cost_center cc ON f.cost_center_key = cc.cost_center_key
WHERE
    cc.cost_center_key IS NULL;

-- ============================================================================
-- Missing Department
-- ============================================================================
SELECT
    f.gl_entry_key,
    f.department_key
FROM
    warehouse.fact_gl f
    LEFT JOIN warehouse.dim_department d ON f.department_key = d.department_key
WHERE
    d.department_key IS NULL;

-- ============================================================================
-- Missing Currency
-- ============================================================================
SELECT
    f.gl_entry_key,
    f.currency_key
FROM
    warehouse.fact_gl f
    LEFT JOIN warehouse.dim_currency cur ON f.currency_key = cur.currency_key
WHERE
    cur.currency_key IS NULL;

-- ============================================================================
-- Missing Posting Date
-- ============================================================================
SELECT
    f.gl_entry_key,
    f.posting_date_key
FROM
    warehouse.fact_gl f
    LEFT JOIN warehouse.dim_date dt ON f.posting_date_key = dt.date_key
WHERE
    dt.date_key IS NULL;

-- ============================================================================
-- Missing Document Date
-- ============================================================================
SELECT
    f.gl_entry_key,
    f.document_date_key
FROM
    warehouse.fact_gl f
    LEFT JOIN warehouse.dim_date dt ON f.document_date_key = dt.date_key
WHERE
    dt.date_key IS NULL;

-- ============================================================================
-- Missing Due Date
-- ============================================================================
SELECT
    f.gl_entry_key,
    f.due_date_key
FROM
    warehouse.fact_gl f
    LEFT JOIN warehouse.dim_date dt ON f.due_date_key = dt.date_key
WHERE
    dt.date_key IS NULL;