SELECT DISTINCT
    document_type
FROM
    warehouse.fact_gl
WHERE
    supplier_key IS NOT NULL;

SELECT DISTINCT
    document_type
FROM
    warehouse.fact_gl
WHERE
    customer_key IS NOT NULL;

SELECT
    *
FROM
    warehouse.fact_gl
WHERE
    debit_amount = 0
    AND credit_amount = 0;

SELECT
    *
FROM
    warehouse.fact_gl
WHERE
    account_key IS NULL
    OR company_key IS NULL
    OR currency_key IS NULL;