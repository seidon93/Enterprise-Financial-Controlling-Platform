/*
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : validation_statistics.sql
Object Type     : Validation Script
Layer           : Database Validation
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Provides statistical overview of generated accounting data.
===============================================================================
*/
-- ============================================================================
-- 1. Total journal rows
-- ============================================================================
SELECT
    COUNT(*) AS total_rows
FROM
    warehouse.fact_gl;

-- ============================================================================
-- 2. Documents by type
-- ============================================================================
SELECT
    document_type,
    COUNT(DISTINCT document_number) AS documents,
    COUNT(*) AS journal_rows
FROM
    warehouse.fact_gl
GROUP BY
    document_type
ORDER BY
    document_type;

-- ============================================================================
-- 3. Companies
-- ============================================================================
SELECT
    c.company_code,
    COUNT(*) AS journal_rows
FROM
    warehouse.fact_gl f
    JOIN warehouse.dim_company c ON f.company_key = c.company_key
GROUP BY
    c.company_code
ORDER BY
    c.company_code;

-- ============================================================================
-- 4. Accounts
-- ============================================================================
SELECT
    a.account_number,
    COUNT(*) AS journal_rows
FROM
    warehouse.fact_gl f
    JOIN warehouse.dim_account a ON f.account_key = a.account_key
GROUP BY
    a.account_number
ORDER BY
    a.account_number;

-- ============================================================================
-- 5. Currencies
-- ============================================================================
SELECT
    c.currency_code,
    COUNT(*) AS journal_rows
FROM
    warehouse.fact_gl f
    JOIN warehouse.dim_currency c ON f.currency_key = c.currency_key
GROUP BY
    c.currency_code
ORDER BY
    c.currency_code;

-- ============================================================================
-- 6. Date range
-- ============================================================================
SELECT
    MIN(d.full_date) AS first_posting_date,
    MAX(d.full_date) AS last_posting_date
FROM
    warehouse.fact_gl f
    JOIN warehouse.dim_date d ON f.posting_date_key = d.date_key;

-- ============================================================================
-- 7. Batch statistics
-- ============================================================================
SELECT
    batch_id,
    COUNT(*) AS journal_rows
FROM
    warehouse.fact_gl
GROUP BY
    batch_id
ORDER BY
    batch_id DESC;

-- ============================================================================
-- 8. Average journal lines per document
-- ============================================================================
SELECT
    document_type,
    ROUND(AVG(line_count), 2) AS average_lines
FROM
    (
        SELECT
            document_type,
            document_number,
            COUNT(*) AS line_count
        FROM
            warehouse.fact_gl
        GROUP BY
            document_type,
            document_number
    ) t
GROUP BY
    document_type
ORDER BY
    document_type;