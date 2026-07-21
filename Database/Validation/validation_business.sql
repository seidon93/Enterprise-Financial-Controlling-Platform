/******************************************************************************
EFAP Business Validation
******************************************************************************/
------------------------------------------------------------------------------
-- 1. Documents by type
------------------------------------------------------------------------------
SELECT
    document_type,
    COUNT(DISTINCT document_number) AS documents
FROM
    warehouse.fact_gl
GROUP BY
    document_type
ORDER BY
    document_type;

------------------------------------------------------------------------------
-- 2. Journal lines by document type
------------------------------------------------------------------------------
SELECT
    document_type,
    COUNT(*) AS journal_lines
FROM
    warehouse.fact_gl
GROUP BY
    document_type
ORDER BY
    document_type;

------------------------------------------------------------------------------
-- 3. Supplier documents without supplier
------------------------------------------------------------------------------
SELECT
    COUNT(*) AS missing_supplier
FROM
    warehouse.fact_gl
WHERE
    document_type IN ('AP', 'SP')
    AND supplier_key IS NULL;

------------------------------------------------------------------------------
-- 4. Customer documents without customer
------------------------------------------------------------------------------
SELECT
    COUNT(*) AS missing_customer
FROM
    warehouse.fact_gl
WHERE
    document_type IN ('AR', 'CP')
    AND customer_key IS NULL;

------------------------------------------------------------------------------
-- 5. Balance check
------------------------------------------------------------------------------
SELECT
    document_number,
    ROUND(SUM(debit_amount), 2) AS debit,
    ROUND(SUM(credit_amount), 2) AS credit
FROM
    warehouse.fact_gl
GROUP BY
    document_number
HAVING
    ROUND(SUM(debit_amount), 2) <> ROUND(SUM(credit_amount), 2);

------------------------------------------------------------------------------
-- 6. Purchase account structure
------------------------------------------------------------------------------
SELECT
    a.account_number,
    COUNT(*) rows
FROM
    warehouse.fact_gl f
    JOIN warehouse.dim_account a ON f.account_key = a.account_key
WHERE
    f.document_type = 'AP'
GROUP BY
    a.account_number
ORDER BY
    a.account_number;

------------------------------------------------------------------------------
-- 7. Sales account structure
------------------------------------------------------------------------------
SELECT
    a.account_number,
    COUNT(*) rows
FROM
    warehouse.fact_gl f
    JOIN warehouse.dim_account a ON f.account_key = a.account_key
WHERE
    f.document_type = 'AR'
GROUP BY
    a.account_number
ORDER BY
    a.account_number;

------------------------------------------------------------------------------
-- 8. Supplier Payments account structure
------------------------------------------------------------------------------
SELECT
    a.account_number,
    COUNT(*) rows
FROM
    warehouse.fact_gl f
    JOIN warehouse.dim_account a ON f.account_key = a.account_key
WHERE
    f.document_type = 'SP'
GROUP BY
    a.account_number
ORDER BY
    a.account_number;

------------------------------------------------------------------------------
-- 9. Customer Payments account structure
------------------------------------------------------------------------------
SELECT
    a.account_number,
    COUNT(*) rows
FROM
    warehouse.fact_gl f
    JOIN warehouse.dim_account a ON f.account_key = a.account_key
WHERE
    f.document_type = 'CP'
GROUP BY
    a.account_number
ORDER BY
    a.account_number;

------------------------------------------------------------------------------
-- 10. Posting date coverage
------------------------------------------------------------------------------
SELECT
    MIN(d.full_date) AS first_posting,
    MAX(d.full_date) AS last_posting
FROM
    warehouse.fact_gl f
    JOIN warehouse.dim_date d ON f.posting_date_key = d.date_key;