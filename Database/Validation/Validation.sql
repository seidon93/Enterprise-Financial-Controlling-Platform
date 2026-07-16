-- summary report
SELECT document_type,
    COUNT(DISTINCT document_number) AS documents,
    COUNT(*) AS journal_rows
FROM warehouse.fact_gl
GROUP BY document_type
ORDER BY document_type;
-- check for balancing document
SELECT document_number,
    ROUND(SUM(debit_amount), 2) AS debit,
    ROUND(SUM(credit_amount), 2) AS credit
FROM warehouse.fact_gl
GROUP BY document_number
HAVING ROUND(SUM(debit_amount), 2) <> ROUND(SUM(credit_amount), 2);
--check for number of documents by document type
SELECT document_type,
    document_number,
    COUNT(*) AS lines
FROM warehouse.fact_gl
GROUP BY document_type,
    document_number
ORDER BY document_type,
    lines DESC;
--count documents by document type
SELECT account_number,
    COUNT(*) AS rows
FROM warehouse.dim_account
GROUP BY account_number
ORDER BY account_number;
--check for number of companies
SELECT company_code,
    COUNT(*) AS rows
FROM warehouse.dim_company
GROUP BY company_code
ORDER BY company_code;
--check for number of currencies
SELECT currency_code,
    COUNT(*) AS rows
FROM warehouse.dim_currency
GROUP BY currency_code
ORDER BY currency_code;
--check for number of batches
SELECT batch_id,
    COUNT(*) AS rows
FROM warehouse.fact_gl
GROUP BY batch_id
ORDER BY batch_id DESC;
--check for number of posting dates
SELECT MIN(d.full_date) AS first_date,
    MAX(d.full_date) AS last_date
FROM warehouse.fact_gl AS f
    JOIN warehouse.dim_date AS d ON f.posting_date_key = d.date_key;
--check for number of rows in fact_gl
SELECT *
FROM warehouse.fact_gl
LIMIT 1;
--check for columns in fact_gl
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'warehouse'
    AND table_name = 'fact_gl'
ORDER BY ordinal_position;
--count documents by document type
SELECT document_type,
    COUNT(DISTINCT document_number) AS documents
FROM warehouse.fact_gl
GROUP BY document_type
ORDER BY document_type;
--count documents by document type and account number
SELECT f.document_type,
    a.account_number,
    COUNT(*) AS rows
FROM warehouse.fact_gl AS f
    JOIN warehouse.dim_account AS a ON f.account_key = a.account_key
GROUP BY f.document_type,
    a.account_number
ORDER BY f.document_type,
    a.account_number;