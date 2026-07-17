/*
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : validation_balancing.sql
Object Type     : Validation Script
Layer           : Database Validation
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Validates accounting balancing and journal integrity.
===============================================================================
*/


-- ============================================================================
-- 1. Unbalanced documents
-- ============================================================================

SELECT
    document_type,
    document_number,
    ROUND(SUM(debit_amount),2)  AS total_debit,
    ROUND(SUM(credit_amount),2) AS total_credit,
    ROUND(SUM(debit_amount) - SUM(credit_amount),2) AS difference
FROM warehouse.fact_gl
GROUP BY
    document_type,
    document_number
HAVING
    ROUND(SUM(debit_amount),2)
    <>
    ROUND(SUM(credit_amount),2)
ORDER BY
    document_type,
    document_number;


-- ============================================================================
-- 2. Journal lines with both Debit and Credit populated
-- ============================================================================

SELECT
    *
FROM warehouse.fact_gl
WHERE
    debit_amount > 0
AND credit_amount > 0;


-- ============================================================================
-- 3. Journal lines with neither Debit nor Credit
-- ============================================================================

SELECT
    *
FROM warehouse.fact_gl
WHERE
    COALESCE(debit_amount,0)=0
AND COALESCE(credit_amount,0)=0;


-- ============================================================================
-- 4. Negative Debit
-- ============================================================================

SELECT
    *
FROM warehouse.fact_gl
WHERE debit_amount < 0;


-- ============================================================================
-- 5. Negative Credit
-- ============================================================================

SELECT
    *
FROM warehouse.fact_gl
WHERE credit_amount < 0;


-- ============================================================================
-- 6. Negative Local Amount
-- ============================================================================

SELECT
    *
FROM warehouse.fact_gl
WHERE amount_local < 0;


-- ============================================================================
-- 7. Missing Account
-- ============================================================================

SELECT
    *
FROM warehouse.fact_gl
WHERE account_key IS NULL;


-- ============================================================================
-- 8. Missing Company
-- ============================================================================

SELECT
    *
FROM warehouse.fact_gl
WHERE company_key IS NULL;


-- ============================================================================
-- 9. Missing Currency
-- ============================================================================

SELECT
    *
FROM warehouse.fact_gl
WHERE currency_key IS NULL;


-- ============================================================================
-- 10. Missing Posting Date
-- ============================================================================

SELECT
    *
FROM warehouse.fact_gl
WHERE posting_date_key IS NULL;


-- ============================================================================
-- 11. Missing Document Number
-- ============================================================================

SELECT
    *
FROM warehouse.fact_gl
WHERE document_number IS NULL;


-- ============================================================================
-- 12. Missing Batch ID
-- ============================================================================

SELECT
    *
FROM warehouse.fact_gl
WHERE batch_id IS NULL;