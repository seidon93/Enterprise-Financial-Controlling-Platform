SELECT
    COUNT(*)
FROM
    warehouse.fact_gl
WHERE
    customer_key IS NULL
    AND account_key IN (
        SELECT
            account_key
        FROM
            warehouse.dim_account
        WHERE
            account_number = '311'
    );

SELECT
    COUNT(*)
FROM
    warehouse.fact_gl
WHERE
    supplier_key IS NULL
    AND account_key IN (
        SELECT
            account_key
        FROM
            warehouse.dim_account
        WHERE
            account_number = '321'
    );

SELECT
    supplier_code,
    supplier_name
FROM
    warehouse.dim_supplier
LIMIT
    20;

SELECT
    customer_code,
    customer_name
FROM
    warehouse.dim_customer
LIMIT
    20;